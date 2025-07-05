__author__ = 'Grishnak'

from dungeon import dungeon
from dungeon import prefab_dungeon
from dungeon.prefabs import prefabs
import tcod as libtcod
#from game.ecs import systems
from gEngine.utilities.timing import ticker
from gEngine.utilities import console
from gEngine.utilities import status_bar
from gEngine.utilities import messaging
from gEngine.utilities.user_interface import menu
from gEngine.utilities.user_interface import hot_bar

from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget

from gEngine import lights

from game import bark
from game.object import build_objects
from game.object import object

from game.user_interface import inventory
from game.user_interface.widgets import inventory_widget

from game import main_menu

from game.user_interface import hover_description
from game.user_interface.widgets import skill_screen

from game import ranged_combat
from game import input_handler
from game import render
from game.ai_director import ai_director


from game.classes import warrior_skills

from game.debug_modules import module_list, dungeon_status, spawning_tool, reload_module
import os

# todo externalize this data
dungeon_height = 55
dungeon_width = 80
min_room_size = 5
max_room_size = 15
max_rooms = 25
max_room_monsters = 0
max_room_items = 3

def dummy_func():
    pass

class Game:
    def __init__(self, gEngine): # TODO: Break this up into individual functions for setup
        self.active = True
        self.gEngine = gEngine
        self.gEngine.log_open_block("Initializing game...")
        self.keys = self.gEngine.options  # options has direct variables eg: options.key_north
        self.dungeon_generators = []
        self.objects = []
        self.player = None
    #    self.world = esper.World()
        self.ticker = ticker.Ticker()
        self.is_player_turn = False
        self.game_state = None
        self.objects = []
        self.max_depth = 25
        self.fov = None
        self.level = None
        self.levels = []
        # Ui variables
        self.screen_width = self.gEngine.w
        self.screen_height = self.gEngine.h
        self.panel_height = 7
        self.dungeon_height = self.screen_height - self.panel_height - 5
        self.dungeon_width = self.screen_width
        self.bar_width = 20
        self.panel_y = self.screen_height - self.panel_height
        self.message_x = self.bar_width + 2
        self.message_width = self.screen_width
        self.message_height = self.panel_height - 1
        self.inventory_width = 50
        self.light_handler = lights.LightHandler(self.gEngine)
        self.depth = 0
        self.path = None
        # create all of the consoles for drawing and UI
        self.gEngine.log_message("Creating consoles")
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar
        self.message = messaging.Message(self.panel, self.message_height, self.message_width, self.message_x, self.gEngine)

        self.gEngine.log_message("Setting up dungeon Generators")
        self.basic_dungeon = dungeon.BasicDungeon(self.dungeon_height, self.dungeon_width, min_room_size, max_room_size,
                                                  max_rooms, max_room_monsters, max_room_items,
                                                  self.gEngine)
        self.prefab_generator = prefab_dungeon.PrefabGenerator(self.dungeon_width, self.dungeon_height, self.gEngine, self)
        self.dungeon_generators.append(self.basic_dungeon)
        self.dungeon_generators.append(self.prefab_generator)


        self.fov_recompute = True
        self.player_moved = False
        self.monsters = []
        self.build_objects = build_objects.GameObjects(self.gEngine)
        self.newgame = False
        x = 32 / 2
        x = self.gEngine.w / 2 - x
        self.gEngine.log_open_block("Initializing Hotbar")
        self.hotbar = hot_bar.HotBar(x, 0, self.gEngine, self.toolbar)
        z = 1
        index = ord('1')
        for i in range(10):
            if index == ord(':'):
                index = ord('0')
            s = hot_bar.HotBarSlot(None, z + x, self.panel_y - 4, z, chr(index), self.gEngine)
            self.hotbar.add_slot(s)
            z += 3
            index += 1
        self.gEngine.log_message("Hotbar initialized")
        self.gEngine.log_close_block()

        self.big_ui_button_widget = None

        self.player_action = None
        self.bark_manager = bark.BarkManager()
        self.ambient = 0.15
        if not self.gEngine.release:
            self.dev_console = console.Console(self, self.dungeon_width, self.dungeon_height, 'debug')
        self.monster_force_display = [False, 0]
        self.loot_force_display = [False, 0]
        self.ai_director = ai_director.AiDirector(self, self.gEngine)
        self.turns = 0
        self.hover_description = hover_description.HoverDescription(self.dungeon_console, self.gEngine, True)

        path = os.path.abspath('.')
        path = os.path.join(path, 'content')
        back = os.path.join(path, 'img', 'BurntTorch.png')
        fore = os.path.join(path, 'img', 'Torch.png')
        self.player_torch_bar = status_bar.AnimatedStatusBar(back, fore, "torch flame", self.toolbar, self.gEngine, 0, 0)

        self.ranged_ammo_index = None
        self.popup = None
        self.is_player_turn = False
        self.player_inventory_widget = None

        self.passive_skills = []
        self.active_skills = []
        self.weapon_prof_skills = {}
        self.setup_skills()

        self.skill_screen = skill_screen.SkillScreen(self.gEngine, self, 0, 0, self.dungeon_width, self.dungeon_height, "Skills")
        self.skill_screen.active = False


        self.gEngine.log_message("Game fully initialized")
        self.gEngine.log_close_block()



    def setup_ui_modules(self):
        self.big_ui_button_widget = BigUIButtonContainer(self.gEngine, self, 56, self.panel_y-5, 24, 5, "")
        self.big_ui_button_widget.activate()
        self.gEngine.add_module(self.big_ui_button_widget)
        self.big_ui_button_widget.setup()
        self.skill_screen.setup(self)
        self.gEngine.add_module(self.skill_screen)
        self.setup_debug_modules()

        self.gEngine.add_module(self.player_inventory_widget)


    def setup_debug_modules(self):
        d = dungeon_status.DungeonStatus(self.gEngine, self, 5, 6, self.gEngine.SCREEN_WIDTH / 2, 7, "Dungeon Status")
        d.deactivate()
        self.gEngine.add_module(d)

        spawn_tool = spawning_tool.SpawningTools(self.gEngine, self, 0, 0, 18, 9, "Spawning Tools")
        spawn_tool.setup()
        self.gEngine.add_module(spawn_tool)

        # load this module last
        m = module_list.ModuleList(self.gEngine, self, 0, 0, 15, 5, 'Module List')
        m.deactivate()
        self.gEngine.add_module(m)

        r = reload_module.ReloadModule(self.gEngine, x=20, y=0, w=15, h=5, title="Reload Tool")
        r.setup()
        r.deactivate()
        self.gEngine.add_module(r)

    def activate(self):
        self.active = True
        self.gEngine.log_open_block("Game running.")

    def deactivate(self):
        self.active = False

    def toggle(self):
        self.active = not self.active
    def show_player_inventory(self):
        self.toggle()
        self.player_inventory_widget.toggle()
        self.gEngine.bring_module_to_front(self.player_inventory_widget)
        """# show the inventory; if an item is selected, use it
        chosen_item = inventory.inventory(self.dungeon_console, self.player, self)

        if chosen_item is not None:
            chosen_item.item.use(self.player.fighter.inventory, self.player, self)
            self.player_action = 'turn-used'"""

    def on_exit(self):
        self.deactivate()

    def setup_skills(self):
        self.gEngine.log_open_block("Setting up Skills")
        self.setup_weapon_prof_skills()

    def setup_weapon_prof_skills(self):
        self.gEngine.log_message("Weapon Proficiencies...")
        subtype_list = self.build_objects.get_weapon_subtype_list("melee")
        subtype_list = list(set(subtype_list))
        for subtype in subtype_list:
            passive = warrior_skills.WeaponProf(name=subtype, owner=self.player, description= "Proficiency in %s weapons."% subtype)
            self.passive_skills.append(passive)
            self.weapon_prof_skills.update({subtype:passive})


    def handle_input(self, key, mouse):
        turn = input_handler.handle_keys(key, self)


        return turn
    def run(self, key, mouse):
        self.player_moved = False

        # erase all objects at their old locations, before they move
        #for object in self.objects:
        #    object.clear(self.gEngine)

        # Monsters faster than the player, take turns first
        if not self.is_player_turn:
            self.is_player_turn = self.ticker.next_turn(self)
            self.ticker.get_next_tick()

        self.player_action = 'didnt-take-turn'
        if self.player_moved:
            self.gEngine.map_compute_fov(self.player.x, self.player.y)
            self.player_moved = False
        if self.is_player_turn:
            self.player_moved = False

            self.hover_description.reset()
            self.hover_description.update(mouse, self.get_names_under_mouse(), self.dungeon_height)
            self.player_action = self.handle_input(key,mouse)

            if self.player_action == 'exit':
                self.return_to_main_menu()
                return

            if mouse.lbutton:
                if not self.popup and self.player.fighter.gear.get_combat_type() == 'ranged':
                    target = self.check_for_target(mouse.cx, mouse.cy)
                    if target:
                        self.popup = ranged_combat.select_ammo(self.player.x, self.player.y, mouse.cx, mouse.cy,
                                                           self.player, self, target)
                elif self.popup and self.popup.mouse_is_in_console(mouse):
                    if self.ranged_ammo_index:
                        selected_ammo = self.popup.index[self.ranged_ammo_index]
                        if selected_ammo.item.qty > 1:
                            selected_ammo.item.qty -= 1
                        elif selected_ammo.item.qty == 1:
                            self.player.fighter.inventory.remove()
                        multiplier = selected_ammo.item.ammo.damage_multiplier
                        target = self.check_for_target(self.popup.x, self.popup.y)
                        if target:  # possibly redundant
                            ranged_combat.fire_shot(self.player.x, self.player.y, mouse.cx, mouse.cy, self.player, self, target)
                            self.player_action = 'turn-used'
                            self.ranged_ammo_index = None
                            self.popup = None

                    if self.player_action == 'player-moved':
                        self.player_moved = True
                        self.ai_director.add_player_stat('steps moved', 1)

                    if libtcod.console_is_window_closed():
                        self.player_action = 'exit'

                    self.hotbar.update(mouse, key, self)
                    self.bark_manager.update_barks()

            if self.player_action == 'player-moved':
                self.player_moved = True

            self.hotbar.update(mouse, key, self)
            self.bark_manager.update_barks()

            for object in self.objects:
                object.clear(self.gEngine)


            if self.player_action == 'turn-used' or self.player_action == 'player-moved':
                self.ticker.schedule_turn(self.player.fighter.stat.get_stat("Speed"), self.player)
                self.player.fighter.heal_stamina(self.player.fighter.stat.get_stat("StaminaRegen"))
                #print("Player Stamina: %d"%self.player.fighter.stamina)
                self.player.torch.update(self)
                self.is_player_turn = False
                self.turns += 1
                self.ai_director.add_player_stat('turns taken', 1)
                # fast forward until the next object gets its turn
                self.ticker.get_next_tick()

                # TODO - Create system for updating all spells
                if self.monster_force_display[0]:
                    if self.monster_force_display[1] <= 0:
                        self.monster_force_display[0] = False
                        self.message.message("Your detect monster spell has expired.", libtcod.light_cyan)
                    else:
                        self.monster_force_display[1] -= 1

                if self.loot_force_display[0]:
                    if self.loot_force_display[1] <= 0:
                        self.loot_force_display[0] = False
                        self.message.message("Your detect items spell has expired.", libtcod.light_cyan)
                    else:
                        self.loot_force_display[1] -= 1

        render_list = []
        if self.popup:
            self.ranged_ammo_index = self.popup.update(mouse)
            render_list.append(self.popup.render)
        #if self.hover_description:
        #    render_list.append(self.hover_description.render(self, True))
        render.render_all(self, render_list)
        #self.gEngine.console_flush()

        if self.player.fighter.current_xp >= self.player.fighter.xp_to_next_level:
            self.player.fighter.level_up()

    def return_to_main_menu(self):
        self.gEngine.remove_module((self))
        m = main_menu.MainMenu(self.gEngine)
        self.gEngine.add_module(m)

    def setup_player(self):
        fighter_component = object.Fighter(death_function=self.player_death, money=28000, ticker=self.ticker)
        fighter_component.game = self
        self.player = object.Object(self.dungeon_console, 0, 0, '@', 'player',
                                    libtcod.white, blocks=True, fighter=fighter_component)
        self.player.game = self
        self.player.idle_frames = ['player_1', 'player_2', 'player_3', 'player_4', 'player_5']
        self.player.add_idle_animation()

        # TODO Refactor status bars into their own small class with all relevant data attached to it
        # this will help manage bars a bit easier
        self.player_hp_bar = status_bar.StatusBar(self.bar_width, libtcod.light_red,
                                                  libtcod.darker_red, self.panel, gEngine=self.gEngine)

        self.player_resource_bar = status_bar.StatusBar(self.bar_width, libtcod.light_flame,
                                                     libtcod.darker_flame, self.panel, gEngine=self.gEngine)

        self.player_xp_bar = status_bar.StatusBar(self.bar_width, libtcod.light_grey,
                                                  libtcod.dark_grey, self.panel, gEngine=self.gEngine)


        self.ticker.schedule_turn(10, self.player)
        # fast forward until the next object gets its turn
        self.ticker.get_next_tick()

        torch = object.Torch(self.player)
        self.player.torch = torch

        #self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        self.game_state = 'playing'
        self.ai_director.add_player_stat('gold earned', self.player.fighter.money)
        self.player_inventory_widget = inventory_widget.Inventory(self.gEngine, self, w=self.dungeon_width, h=self.dungeon_height, owner=self.player)
        self.player_inventory_widget.deactivate()


    def setup_world(self):
        pass
        #self.world.add_processor(systems.DisplayProcessor())
        #self.world.add_processor(systems.MovementProcessor())

        # self.ticker.get_next_tick()
    def go_to_town(self, first_visit=False):
        self.gEngine.animation_clear_cell()
        self.player.add_idle_animation()

        self.bark_manager.empty(self.gEngine)
        self.objects = []
        self.light_handler.empty()
        l = lights.LightHandler(self.gEngine)
        level = self.prefab_generator.load_level_from_string(prefabs.town, l)
        # level = self.basic_dungeon.make_map(game=self, light_handler=l)
        level.depth = 0
        self.depth = 0
        level.light_handler = l
        for item in self.objects:
            level.objects.append(item)
        #self.levels.append(level)
        self.level = level
        self.fov = self.level.fov_map
        for object in self.objects:
            if object.npc:
                b = bark.Bark(self.gEngine, self.dungeon_console, object, 600.0, object.npc.shop_name)
                self.bark_manager.add_bark(b)
        if not first_visit:
            self.ticker.clear_ticker()
            self.level.objects = []
            self.ticker.schedule_turn(10, self.player)
            for object in self.objects:
                if object.misc:
                    if object.misc.type == 'up':  # place the player at the down stairs on the previous level
                        self.player.x = object.x
                        self.player.y = object.y

    def new_game(self):
        self.setup_player()
        self.go_to_town(True)
        self.gEngine.log_message('Map made')
        self.setup_world()
        self.message.message('Welcome to %s' % self.gEngine.name)
        mes = "%s, %s, %s, %s"%(chr(self.gEngine.fonts['CHAR_ARROW_N']), chr(self.gEngine.fonts['CHAR_ARROW_E']), chr(self.gEngine.fonts['CHAR_ARROW_W']), chr(self.gEngine.fonts['CHAR_ARROW_S']) )
        self.message.message(mes)
        self.path = libtcod.path_new_using_function(self.dungeon_width, self.dungeon_height, path_callback, self)
        #self.newgame = True
        self.gEngine.lightmask_set_ambient(self.ambient)

        render.render_all(self)
        #self.gEngine.mMap = self.level.dungeon

    def new_level(self):
        '''self.gEngine.console_remove_all()
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar
        self.hotbar.reinit_all(self.toolbar)'''
        self.gEngine.animation_clear_cell()
        self.player.add_idle_animation()
        self.ambient -= 0.025
        self.gEngine.lightmask_set_ambient(self.ambient)
        self.bark_manager.empty(self.gEngine)
        left_over_items = 0
        left_over_monsters = 0
        for object in self.objects:
            if object.item:
                left_over_items += 1
            if object.fighter:
                if object != self.player:
                    left_over_monsters += 1
        self.ai_director.add_player_stat('items left behind', left_over_items)
        self.ai_director.add_player_stat('monster left behind', left_over_monsters)
        self.ticker.clear_ticker()
        self.level.objects = []
        for objects in self.objects:
            self.level.objects.append(objects)
        self.objects = []

        l = lights.LightHandler(self.gEngine)
        self.ai_director.spawn_nodes.clear()
        # level = self.basic_dungeon.make_map(game=self, light_handler=l)
        level = self.prefab_generator.level_from_prefabs(light_handler=l)

        fast_level_speed = self.ai_director.get_player_stat('fastest level')
        long_level_speed = self.ai_director.get_player_stat('longest level')
        if self.turns < fast_level_speed:
            self.ai_director.add_player_stat('fastest level', self.turns, True)

        if self.turns > long_level_speed:
            self.ai_director.add_player_stat('longest level', self.turns, True)
        if self.depth == 1:
            self.ai_director.add_player_stat('fastest level', self.turns, True)
        self.turns = 0
        level.depth = self.depth + 1
        self.depth += 1
        if self.depth > 0:
            r = libtcod.random_get_int(0, 0, len(bark.player_new_level_barks) - 1)
            b = bark.Bark(self.gEngine, self.dungeon_console, self.player, 3.0, bark.player_new_level_barks[r])
            self.bark_manager.add_bark(b)
        level.light_handler = l
        self.levels.append(level)
        self.level = level
        self.fov = self.level.fov_map

        # self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        for object in self.objects:
            if object.misc:
                if object.misc.type == 'up':  # place the player at the down stairs on the previous level
                    self.player.x = object.x
                    self.player.y = object.y
        #self.objects = []
        self.game_state = 'playing'
        self.ai_director.take_turn()
        render.render_all(self)
        self.ticker.schedule_turn(10, self.player)
        self.ticker.get_next_tick()
        render.render_all(self)

    def prev_level(self):
        self.objects = []
        self.ticker.clear_ticker()
        self.depth -= 1
        self.level = None
        self.level = self.levels[self.depth-1]
        self.level.new_level()

        for object in self.level.objects:
            self.objects.append(object)
            if object.misc:
                if object.misc.type == 'down':  # place the player at the down stairs on the previous level
                    self.player.x = object.x
                    self.player.y = object.y

        # self.objects = self.level.objects
        self.fov = self.level.fov_map
        self.game_state = 'playing'
        render.render_all(self)
        self.ticker.schedule_turn(10, self.player)
        # add in spawn node or monster turns
        # self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)

    def check_for_target(self, x, y):
        for object in self.objects:
            if object.fighter and object.x == x and object.y == y:
                return object
            if object.npc and object.x == x and object.y == y:
                return object
        return None

    def player_death(self, player, game=None):
        # the game ended!
        self.message.message('You died! Press Escape to return to the main menu.', 1)
        self.game_state = 'dead'

        # for added effect, transform the player into a corpse!
        self.player.char = '%'
        self.player.color = libtcod.dark_red
        self.ai_director.dump_data()
        #self.gEngine.console_remove_console(self.dungeon_console)

    def get_names_under_mouse(self):
        # return a string with the names of all objects under the mouse
        #mouse = libtcod.mouse_get_status()
        key, mouse = self.gEngine.handle_input()
        (x, y) = (mouse.cx, mouse.cy)
        names = []
        # create a list with the names of all objects at the mouse's coordinates and in FOV
        #names = [obj.name for obj in self.objects
        #         if obj.x == x and obj.y == y and libtcod.map_is_in_fov(self.fov, obj.x, obj.y)]
        for obj in self.objects:
            if self.gEngine.map_is_in_fov(obj.x, obj.y):
                if obj.x == x and obj.y == y:
                    names = obj.hover_description()
                if obj.x == x and obj.y == y and not names:
                    names = [obj.name]
        return names

    def get_names_under_player(self):
        if self.player_moved:
            names = []
            for object in self.objects:
                if object is not self.player:
                    if object.distance_to(self.player) == 0:
                        names.append(menu.color_text(object.name, object.color))

            n = len(names)
            if n > 0:
                names = ', '.join(names)
                if n == 1:
                    msg = menu.color_text('You see a ', libtcod.white)
                    msg += names
                    msg += menu.color_text(', here.', libtcod.white)
                else:
                    msg = menu.color_text('You see ', libtcod.white)
                    msg += names
                    msg += menu.color_text(' here.', libtcod.white)
                self.message.message(msg, 0)

    def big_ui_button_help(self):
        self.gEngine.toggle_module(self.gEngine.get_module_by_name("HelpPopup"))

    def big_ui_button_inventory(self):
        self.show_player_inventory()
        """chosen_item = inventory.inventory(self.dungeon_console, self.player, self)

        if chosen_item is not None:
            chosen_item.item.use(self.player.fighter.inventory, self.player, self)
            self.player_action = 'turn-used'"""

    def big_ui_button_skills(self):
        mod = self.gEngine.get_module_by_name("SkillScreen")
        if mod:
            mod.activate()
            self.deactivate()
            mod.setup(self)
            self.gEngine.bring_module_to_front(mod)

    def small_ui_button_debug(self):
        mod = self.gEngine.get_module_by_name("ModuleList")
        if mod:
            self.gEngine.toggle_module(mod)
            if mod.active:
                self.gEngine.bring_module_to_front(mod)
        mod = self.gEngine.get_module_by_name("ReloadModule")
        if mod:
            self.gEngine.toggle_module(mod)
            if mod.active:
                self.gEngine.bring_module_to_front(mod)
def path_callback(xFrom, yFrom, xTo, yTo, userData):
    for obj in userData.objects:
        if obj.is_blocked(xTo, yTo, userData.level.dungeon, userData.objects):
            return 0.0
        else:
            return 1.0
    m = userData.Map.map
    if m[xTo][yTo].blocked:
        return 0.0
    else:
        return 1.0


class BigUIButton(button_widget.BigButtonWidget):
    def __init__(self, parent, x, y, function=None, passable=None, button_cells=None):
        if button_cells is None:
            button_cells = ['','','','']
        super().__init__(parent, x, y, button_cells, function, passable)
        self.height = 2
        self.width = 2
        self.char_a = button_cells[0]
        self.char_b = button_cells[1]
        self.char_c = button_cells[2]
        self.char_d = button_cells[3]
        self.untriggered_color = libtcod.white
        self.triggered_color = libtcod.green
        self.background_color = libtcod.black
        self.fore_color = libtcod.white
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)

    def pre_draw_widget(self):
        if self.active:
            self.gEngine.console_set_default_background(self.con, self.background_color)
            self.gEngine.console_put_char_ex(self.con, 0, 0, self.char_a, self.fore_color, self.background_color)
            self.gEngine.console_put_char_ex(self.con, 1, 0, self.char_b, self.fore_color, self.background_color)
            self.gEngine.console_put_char_ex(self.con, 0, 1, self.char_c, self.fore_color, self.background_color)
            self.gEngine.console_put_char_ex(self.con, 1, 1, self.char_d, self.fore_color, self.background_color)

    def color_button_text(self, color):
        pass

    def basic_mouse_input(self, mouse):
        if self.mouse_is_in_console(mouse):
            self.fore_color = libtcod.dark_orange
            if mouse.lbutton:
                return self.trigger()
        else:
            if not self.triggered:
                self.fore_color = self.untriggered_color
            else:
                self.fore_color = self.triggered_color

class BigUIButtonContainer(window_widget.StaticWindowWidget):
    def __init__(self,gEngine, game, x, y, w, h, title):
        super().__init__(gEngine, game, x, y, w, h, title)
        self.buttons = []
        #self.buttons.append(BigUIButton(self, 1, 1, dummy_func, button_cells=cells))

    def update(self, key, mouse):
        if self.active:
            for button in self.buttons:
                if button:
                    button.run(key, mouse)
                pass
    def setup(self):
        cells = ['inv_a', 'inv_b', 'inv_c', 'inv_d']
        f = self.game.big_ui_button_inventory
        self.buttons.append(BigUIButton(self, 1, 1, f, button_cells=cells))

        f = self.game.big_ui_button_help
        cells = ['help_a', 'help_b', 'help_c', 'help_d']
        self.buttons.append(BigUIButton(self, 4, 1, f, button_cells=cells))

        f = self.game.big_ui_button_skills
        cells = ['skill_a', 'skill_b', 'skill_c', 'skill_d']
        self.buttons.append(BigUIButton(self, 7, 1, f, button_cells=cells))

        f = self.game.small_ui_button_debug
        self.buttons.append(button_widget.TextButtonWidget(self, 22, 3, "D", f))