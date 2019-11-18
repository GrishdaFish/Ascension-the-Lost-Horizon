__author__ = 'Grishnak'
from dungeon import dungeon
import tcod as libtcod
import esper
from game.ecs import components
from game.ecs import systems
from gEngine.utilities.timing import ticker
from gEngine.utilities import status_bar
from gEngine.utilities import messaging
from gEngine.utilities.user_interface import menu
from gEngine.utilities.user_interface import hot_bar
from game import lights
from game import bark
from game.object import build_objects
from game.object import object
from game.user_interface import inventory
from game.user_interface import character
from game.user_interface import menus
from game import ranged_combat
# todo externalize this data
dungeon_height = 55
dungeon_width = 80
min_room_size = 10
max_room_size = 15
max_rooms = 15
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

        self.path = None
        # create all of the consoles for drawing and UI
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar

        self.basic_dungeon = dungeon.BasicDungeon(self.dungeon_height, self.dungeon_width, min_room_size, max_room_size,
                                                  max_rooms, max_room_monsters, max_room_items,
                                                  self.gEngine)
        self.dungeon_generators.append(self.basic_dungeon)
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
        r = libtcod.random_get_int(0, 0, len(bark.player_new_level_barks)-1)
        b = bark.Bark(self.gEngine, self.dungeon_console, self.player, 3.0, bark.player_new_level_barks[r])
        self.bark_manager.add_bark(b)

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

                    self.player_action = self.handle_keys(key)
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



                    self.render_all()
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
                                                  libtcod.darker_red,
                                                  self.panel, type='hp', gEngine=self.gEngine)
        self.player_xp_bar = status_bar.StatusBar(self.player.fighter, self.bar_width, libtcod.light_grey,
                                                  libtcod.dark_grey,
                                                  self.panel, type='xp', gEngine=self.gEngine)

        self.ticker.schedule_turn(10, self.player)
        #self.ticker.schedule_turn(self.light_handler.tick_speed, self.light_handler)
        self.game_state = 'playing'

    def setup_world(self):
        self.world.add_processor(systems.DisplayProcessor())
        self.world.add_processor(systems.MovementProcessor())

        # self.ticker.get_next_tick()

    def new_game(self):
        self.setup_player()
        self.level = self.basic_dungeon.make_map(game=self)
        self.level.depth = 1
        self.fov = self.level.fov_map
        self.gEngine.log_message('Map made')
        self.setup_world()
        self.message.message('Welcome to %s' % self.gEngine.name)
        self.path = libtcod.path_new_using_function(self.dungeon_width, self.dungeon_height, path_callback, self)
        self.newgame = True
        #self.gEngine.mMap = self.level.dungeon

    def handle_keys(self, key):
        turn = self.handle_misc(key)
        if turn == 'exit':
            return turn
        turn = 'didnt-take-turn'

        if self.game_state == 'playing':
            turn = self.handle_movement(key)
            turn = self.handle_pickup(key, turn)
            turn = self.handle_character(key, turn)
            turn = self.handle_inventory(key, turn)
            turn = self.handle_drop(key, turn)
            turn = self.handle_stairs(key, turn)
            return turn
        return turn

    def get_move_direction(self, key):
        move_keys = {self.keys.key_north: (0, -1),
                     self.keys.key_south: (0, 1),
                     self.keys.key_east: (1, 0),
                     self.keys.key_west: (-1, 0),
                     }
        px, py = move_keys[key]
        direction = ""
        if key == self.keys.key_north:
            direction = "north"
        if key == self.keys.key_south:
            direction = "south"
        if key == self.keys.key_east:
            direction = "east"
        if key == self.keys.key_west:
            direction = "west"
        return px, py, direction

    def handle_movement(self, key):
        move_keys = {self.keys.key_north: (0, -1),
                     self.keys.key_south: (0, 1),
                     self.keys.key_east: (1, 0),
                     self.keys.key_west: (-1, 0),
                     }
        if key.vk in move_keys:
            px, py, d = self.get_move_direction(key.vk)
            return self.player_move_or_attack(px, py, d)

        # for char based keys, 'w','a','s','d', etc..
        elif chr(key.c) in move_keys:
            px, py, d = self.get_move_direction(chr(key.c))
            return self.player_move_or_attack(px, py, d)

        return 'didnt-take-turn'

    def handle_pickup(self, key, turn):
        if key.c is ord(self.keys.key_pickup):
            for object in self.objects:
                if object.x == self.player.x and object.y == self.player.y and object.item:
                    object.item.pick_up(self.player.fighter.inventory, self)
                    turn = 'turn-used'
        return turn

    def handle_character(self, key, turn):
        if key.c is ord(self.keys.key_character):
            character.character_info(0, self.screen_width, self.screen_height, self)
        return turn

    def handle_inventory(self, key, turn):
        if key.c is ord(self.keys.key_inventory):
            # show the inventory; if an item is selected, use it
            chosen_item = inventory.inventory(self.dungeon_console, self.player, self)

            if chosen_item is not None:
                chosen_item.item.use(self.player.fighter.inventory, self.player, self)
                turn = 'turn-used'
        return turn

    def handle_drop(self, key, turn):
        if key.c is ord(self.keys.key_drop):
            chosen_item = inventory.inventory(self.dungeon_console, self.player, self)
            if chosen_item is not None:
                if chosen_item in self.player.fighter.inventory:
                    chosen_item.objects = self.objects
                    chosen_item.item.drop(self.player.fighter.inventory, self.player)
                    chosen_item.send_to_back()
                turn = 'turn-used'
        return turn

    def handle_misc(self, key):
        turn = None
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            # Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
            turn = None

        if key.c is ord('`') or key.c is ord('~'):
            # self.console.run_console()
            turn = None

        if key.vk == libtcod.KEY_ESCAPE:
            turn = self.handle_quit()

        return turn

    def handle_quit(self, key):
        return 'quit'
        # elif key.vk == libtcod.KEY_ESCAPE:
        #    message = 'Return to main menu?'
        #    w = len(message) * 2
        #    d_box = DialogBox(self, w, 10, 20, 20, message, type='option', con=self.con)
        #    first = True
        #    while 1:
        #        confirm = d_box.display_box()
        #        if confirm == 1:
        #            d_box.destroy_box()
        #            return 'exit'  # exit game
        #        elif confirm == 0:
        #            if first:
        #                first = False
        #            else:
        #                d_box.destroy_box()
        #                return 'didnt-take-turn'

    def handle_stairs(self, key, turn):
        if key.text == '<':
            for object in self.objects:
                if object.x == self.player.x and object.y == self.player.y and object.misc:
                    if object.misc.type == 'up':
                        if self.level.depth == 1:
                            menus.town_menu(self.dungeon_console, 'Welcome to Town', self, self.inventory_width,
                                            self.gEngine.h,
                                            self.gEngine.w)
                            turn = 'turn-used'
                        else:
                            #self.depth -= 1
                            #self.load_level(self.depth, 'up')

                            turn = 'turn-used'

        if key.text == '>':
            for object in self.objects:
                if object.x == self.player.x and object.y == self.player.y and object.misc:
                    if object.misc.type == 'down':
                        # save previous level
                        # self.current_dungeon.append(Level(self.Map.map, self.objects, self.Map.depth))
                        #self.depth += 1
                        #self.load_level(self.depth, 'down')
                        # self.new_level()
                        turn = 'turn-used'
        return turn

    def check_for_target(self, x, y):
        for object in self.objects:
            if object.fighter and object.x == x and object.y == y:
                return object
        return None

    def player_move_or_attack(self, dx, dy, direction=None):
        # the coordinates the player is moving to/attacking
        x = self.player.x + dx
        y = self.player.y + dy

        # try to find an attackable object there
        target = self.check_for_target(x, y)

        # attack if target found, move otherwise
        if target is not None:
            self.player.fighter.attack(target, player=True, direction=direction, game=self)
            return 'turn-used'
        else:
            self.player.move(dx, dy, self.level.dungeon, self.objects)
            self.fov_recompute = True
            return 'player-moved'

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

    def render_all(self):  # break this up to render ui and other elements separately
        self.gEngine.console_clear(self.dungeon_console)
        if self.fov_recompute:
            self.fov_recompute = False
            libtcod.map_compute_fov(self.fov, self.player.x, self.player.y)
        self.update_lighting()

        #self.gEngine.map_draw_fast(self.dungeon_console, self.player.x, self.player.y)
        self.gEngine.map_draw(self.dungeon_console, self.player.x, self.player.y)

        self.draw_objects()

        # self.world.process()

        self.draw_user_interface()

        self.get_names_under_player()

        self.message.flush_messages()

        self.bark_manager.render_barks()

        self.render_consoles()

    def update_lighting(self):
        self.gEngine.lightmask_reset()
        self.light_handler.update()
        self.light_handler.render()
        r = libtcod.random_get_float(0, -0.025, 0.025)
        self.gEngine.lightmask_add_light(self.player.x, self.player.y, (0.65 + r))
        for object in self.objects:
            if object.fighter:
                r = libtcod.random_get_float(0, -0.025, 0.025)
                self.gEngine.lightmask_add_light(object.x, object.y, (0.4 + r))

        self.gEngine.particle_update(self.level.dungeon)
        self.gEngine.lightmask_compute(self.level.dungeon)

    def draw_objects(self):
        for object in self.objects:
            if object.misc:
                if object.misc.type == 'up' or object.misc.type == 'down':
                    # Draw stairs if they are already found
                    if self.gEngine.map_is_explored(object.x, object.y):
                        object.draw(self.fov, self.gEngine, force_display=True)
                else:
                    object.draw(self.fov, self.gEngine)
            else:
                object.draw(self.fov, self.gEngine)
        self.player.draw(self.fov, self.gEngine)

    def draw_user_interface(self):
        r, g, b = libtcod.black
        self.gEngine.console_set_default_background(self.panel, r, g, b)
        self.gEngine.console_clear(self.panel)

        self.player_hp_bar.render(1, 1, self.gEngine)
        self.player_xp_bar.render(1, 3, self.gEngine)

        r, g, b = libtcod.light_gray
        self.gEngine.console_set_default_foreground(self.panel, r, g, b)
        self.gEngine.console_set_alignment(self.panel, libtcod.LEFT)
        self.gEngine.console_set_default_background(0, r, g, b)
        self.gEngine.console_print(self.panel, 1, 5, "(%dfps) Depth: %d" % (libtcod.sys_get_fps(), self.level.depth))
        self.gEngine.console_print(self.panel, 1, 0, self.get_names_under_mouse())

    def render_consoles(self):
        self.hotbar.render()

        self.gEngine.console_blit(self.dungeon_console, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
        self.gEngine.console_blit(self.toolbar, 0, 0, self.gEngine.w, 5, 0, 0, self.panel_y - 5, 1.0, 1.0)
        self.gEngine.console_blit(self.panel, 0, 0, self.screen_width, self.panel_height, 0, 0, self.panel_y, 1.0, 1.0)


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
