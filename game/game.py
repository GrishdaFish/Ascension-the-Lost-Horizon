__author__ = 'Grishnak'
from copy import deepcopy
from dungeon import dungeon
from dungeon import prefab_dungeon
from dungeon.prefabs import prefabs
import tcod as libtcod
import esper
from game.ecs import systems
from gEngine.utilities.timing import ticker
from gEngine.utilities import status_bar
from gEngine.utilities import messaging
from gEngine.utilities.user_interface import menu
from gEngine.utilities.user_interface import hot_bar
from gEngine.utilities.user_interface import dialog_box
from gEngine import lights
from game import bark
from game.object import build_objects
from game.object import object
from game.user_interface import inventory
from game.user_interface import character
from game.user_interface import menus
from game import ranged_combat
from game import input_handler
from game import render
# todo externalize this data
dungeon_height = 55
dungeon_width = 80
min_room_size = 5
max_room_size = 15
max_rooms = 25
max_room_monsters = 0
max_room_items = 3


class Game:
    def __init__(self, gEngine):
        self.active = True
        self.gEngine = gEngine
        self.keys = self.gEngine.options  # options has direct variables eg: options.key_north
        self.dungeon_generators = []
        self.objects = []
        self.player = None
        self.world = esper.World()
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
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar

        self.basic_dungeon = dungeon.BasicDungeon(self.dungeon_height, self.dungeon_width, min_room_size, max_room_size,
                                                  max_rooms, max_room_monsters, max_room_items,
                                                  self.gEngine)
        self.prefab_generator = prefab_dungeon.PrefabGenerator(self.dungeon_width, self.dungeon_height, self.gEngine, self)
        self.dungeon_generators.append(self.basic_dungeon)
        self.dungeon_generators.append(self.prefab_generator)
        self.message = messaging.Message(self.panel, self.message_height, self.message_width,
                                         self.message_x, self.gEngine)

        self.fov_recompute = True
        self.player_moved = False
        self.monsters = []
        self.build_objects = build_objects.GameObjects()
        self.newgame = False
        x = 32 / 2
        x = self.gEngine.w / 2 - x
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
        self.player_action = None
        self.bark_manager = bark.BarkManager()
        self.ambient = 0.15

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def run(self, key, mouse):
        #close = self.handle_keys(key)
        #if close is True:
        #    return True
        if self.newgame:
            menus.town_menu(self.dungeon_console, 'Welcome to Town', self, self.inventory_width, self.gEngine.h,
                            self.gEngine.w)
            self.newgame = False


        while not libtcod.console_is_window_closed():
            libtcod.map_compute_fov(self.fov, self.player.x, self.player.y)

            #self.render_all()
            self.player_moved = False
            #self.gEngine.console_flush()
            key = libtcod.Key()
            mouse = libtcod.Mouse()
            libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)

            # erase all objects at their old locations, before they move
            for object in self.objects:
                object.clear(self.gEngine)

            # for particle in self.particles:
            #    particle.clear(self.gEngine)

            # Monsters faster than the player, take turns first
            is_player_turn = self.ticker.next_turn(self)

            # self.hotbar.update(mouse, key, self)

            self.player_action = 'didnt-take-turn'
            if is_player_turn:
                self.player_moved = False
                #self.player_action = self.handle_keys(key)
                ##Make sure the player takes his turn before continuing
                ##Need to have certain actions take certain speeds
                ##moving takes up the full speed, attacking dependant on weapon
                ##inventory actions depend on what was done
                while self.player_action == 'didnt-take-turn':

                    key = libtcod.Key()
                    mouse = libtcod.Mouse()
                    libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)

                    self.player_action = input_handler.handle_keys(key, self)#self.handle_keys(key)
                    if mouse.lbutton_pressed:
                        #intensity = 1.0 # libtcod.random_get_float(0, 1.0, 1.5)
                        #l = lights.Light(mouse.cx, mouse.cy, self.light_handler, flicker=True, decay=0.005)
                        # c = [libtcod.white, libtcod.orange]
                        # l.staged_lerp(2.0, 1.6, 0.05, 0.0095, c)
                        #l.randomize()
                        #l.ramped_light(0.1, 1.5, 0.0005, False)
                        #self.light_handler.add_light(l)
                        target = self.check_for_target(mouse.cx, mouse.cy)
                        ranged_combat.fire_shot(self.player.x, self.player.y, mouse.cx, mouse.cy, self.player, self, target)
                        self.player_action = 'turn-used'

                    if self.player_action == 'player-moved':
                        self.player_moved = True


                    if libtcod.console_is_window_closed():
                        self.player_action = 'exit'

                    self.hotbar.update(mouse, key, self)
                    self.bark_manager.update_barks()

                    for object in self.objects:
                        object.clear(self.gEngine)

                    if self.player_action == 'turn-used' or self.player_action == 'player-moved':
                        self.ticker.schedule_turn(self.player.fighter.speed, self.player)
                        self.player.torch.update(self)


                    render.render_all(self)# self.render_all()
                    self.gEngine.console_flush()
                #if self.player_action == 'turn-used' or self.player_action == 'player-moved':
                #    self.ticker.schedule_turn(self.player.fighter.speed, self.player)

            if self.player_action == 'exit' or libtcod.console_is_window_closed():
                # self.logger.log.info('Exiting and saving game..')
                # self.save_game()
                return True

            # fast forward until the next object gets its turn
            self.ticker.get_next_tick()
            if self.player.fighter.current_xp >= self.player.fighter.xp_to_next_level:
                self.player.fighter.level_up()
    # check for game state = dead

    def setup_player(self):
        fighter_component = object.Fighter(hp=90, defense=2, power=5, death_function=self.player_death, money=800,
                                           speed=10)
        self.player = object.Object(self.dungeon_console, 0, 0, '@', 'player',
                                    libtcod.white, blocks=True, fighter=fighter_component)

        self.player_hp_bar = status_bar.StatusBar(self.player.fighter, self.bar_width, libtcod.light_red,
                                                  libtcod.darker_red, self.panel, type='hp', gEngine=self.gEngine)

        self.player_torch_bar = status_bar.StatusBar(self.player.fighter, self.bar_width, libtcod.light_flame,
                                                     libtcod.darker_flame, self.panel, type='torch', gEngine=self.gEngine)

        self.player_xp_bar = status_bar.StatusBar(self.player.fighter, self.bar_width, libtcod.light_grey,
                                                  libtcod.dark_grey, self.panel, type='xp', gEngine=self.gEngine)

        self.ticker.schedule_turn(10, self.player)

        torch = object.Torch(self.player)
        self.player.torch = torch

        #self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        self.game_state = 'playing'

    def setup_world(self):
        self.world.add_processor(systems.DisplayProcessor())
        self.world.add_processor(systems.MovementProcessor())

        # self.ticker.get_next_tick()
    def go_to_town(self, first_visit=False):
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
        self.levels.append(level)
        self.level = level
        self.fov = self.level.fov_map
        for object in self.objects:
            if object.npc:
                b = bark.Bark(self.gEngine, self.dungeon_console, object, 30.0, object.npc.shop_name)
                self.bark_manager.add_bark(b)
        if not first_visit:
            self.ticker.clear_ticker()
            self.level.objects = []
            self.ticker.schedule_turn(10, self.player)
            for object in self.objects:
                if object.misc:
                    if object.misc.type == 'down':  # place the player at the down stairs on the previous level
                        self.player.x = object.x
                        self.player.y = object.y

    def new_game(self):
        self.setup_player()
        self.go_to_town(True)
        self.gEngine.log_message('Map made')
        self.setup_world()
        self.message.message('Welcome to %s' % self.gEngine.name)
        self.path = libtcod.path_new_using_function(self.dungeon_width, self.dungeon_height, path_callback, self)
        #self.newgame = True
        self.gEngine.lightmask_set_ambient(self.ambient)

        #self.gEngine.mMap = self.level.dungeon

    def new_level(self):
        '''self.gEngine.console_remove_all()
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar
        self.hotbar.reinit_all(self.toolbar)'''
        self.ambient -= 0.025
        self.gEngine.lightmask_set_ambient(self.ambient)
        self.bark_manager.empty(self.gEngine)

        self.ticker.clear_ticker()
        self.level.objects = []
        for objects in self.objects:
            self.level.objects.append(objects)
        self.objects = []

        l = lights.LightHandler(self.gEngine)
        level = self.basic_dungeon.make_map(game=self, light_handler=l)
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
        self.ticker.schedule_turn(10, self.player)
        # self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        self.game_state = 'playing'

    def prev_level(self):
        # self.gEngine.console_remove_all()
        # self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        # self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        # self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar
        # self.hotbar.reinit_all(self.toolbar)
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
        self.ticker.schedule_turn(10, self.player)
        # add in spawn node or monster turns
        # self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        self.game_state = 'playing'

    def check_for_target(self, x, y):
        for object in self.objects:
            if object.fighter and object.x == x and object.y == y:
                return object
            if object.npc and object.x == x and object.y == y:
                return object
        return None

    def player_death(self, player):
        # the game ended!
        self.message.message('You died!', 1)
        self.game_state = 'dead'

        # for added effect, transform the player into a corpse!
        self.player.char = '%'
        self.player.color = libtcod.dark_red

    def get_names_under_mouse(self):
        # return a string with the names of all objects under the mouse
        mouse = libtcod.mouse_get_status()
        (x, y) = (mouse.cx, mouse.cy)

        # create a list with the names of all objects at the mouse's coordinates and in FOV
        names = [obj.name for obj in self.objects
                 if obj.x == x and obj.y == y and libtcod.map_is_in_fov(self.fov, obj.x, obj.y)]

        names = ', '.join(names)  # join the names, separated by commas
        return names.capitalize()

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
