from game import esc_menu
from game.modules import help_module
from game.user_interface import character
from game.user_interface import inventory
from gEngine.utilities.user_interface import dialog_box
from gEngine.utilities.widget import popups
from gEngine.utilities.widget import button_widget
import tcod as libtcod


close_coords = [
    (0, 1),
    (1, 0),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
    (-1, 0),
    (0, -1)
]
def handle_keys(key, game):
    '''
    Runs through all of the individual key functions
    Remember to return 'Turn' on all functions, even if the action doesnt cause a turn to be used, otherwise AI will
        break because the player will never take a turn

    :param key: they key being pressed
    :param game: the main game instance
    :return: either 'didnt-take'turn or 'turn-used'
    '''
    turn = handle_misc(key, game)
    if turn == 'exit':
        return turn
    turn = 'didnt-take-turn'
    if game.game_state == 'playing':
        turn = handle_movement(key, game, turn)
        turn = handle_pickup(key, game, turn)
        turn = handle_character(key, game, turn)
        turn = handle_char_stats(key, game, turn)
        turn = handle_perk_screen(key, game, turn)
        turn = handle_inventory(key, game, turn)
        turn = handle_drop(key, game, turn)
        turn = handle_stairs(key, game, turn)
        turn = handle_help_screen(key, game, turn)
        turn = handle_open(key, game, turn)

        return turn
    return turn


def handle_misc(key, game):
    turn = None
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        turn = None

    if key.c is ord('`') or key.c is ord('~'):
        game.dev_console.run_console()
        turn = None

    if key.vk == libtcod.KEY_ESCAPE:
        turn = handle_esc_menu(key, game, turn)  # handle_quit(key, game, turn)

    if key.vk == libtcod.KEY_SPACE:
        for item in game.objects:
            if item.misc:
                if item.misc.type == 'down':
                    game.player.x = item.x
                    game.player.y = item.y
    return turn


def handle_movement(key, game, turn):
    move_keys = {game.keys.key_north: (0, -1),
                 game.keys.key_south: (0, 1),
                 game.keys.key_east: (1, 0),
                 game.keys.key_west: (-1, 0),
                 }
    if key.vk in move_keys:
        px, py, d = get_move_direction(key.vk, game)
        return player_move_or_attack(game, px, py, d)

    # for char based keys, 'w','a','s','d', etc..
    elif chr(key.c) in move_keys:
        px, py, d = get_move_direction(chr(key.c), game)
        return player_move_or_attack(game, px, py, d)

    return 'didnt-take-turn'


def handle_pickup(key, game, turn):
    if key.c is ord(game.keys.key_pickup):
        for object in game.objects:
            if object.x == game.player.x and object.y == game.player.y and object.item:
                object.item.pick_up(game.player.fighter.inventory, game)
                turn = 'turn-used'
    return turn


def handle_character(key, game, turn):
    if key.c is ord(game.keys.key_character):
        character.character_info(0, game.screen_width, game.screen_height, game)
    return turn


def handle_char_stats(key, game, turn):
    if key.c is ord(game.keys.key_char_stat):
        character.stat_panel_info(0, game.screen_width, game.screen_height, game)
    return turn


def handle_perk_screen(key, game, turn):
    if key.c is ord(game.keys.key_perks):
        mod = game.gEngine.get_module_by_name("SkillScreen")
        if mod:
            mod.activate()
            game.deactivate()
            mod.setup(game)
            game.gEngine.bring_module_to_front(mod)
    return turn

def handle_inventory(key, game, turn):
    if key.c is ord(game.keys.key_inventory):
        # show the inventory; if an item is selected, use it
        chosen_item = inventory.inventory(game.dungeon_console, game.player, game)

        if chosen_item is not None:
            chosen_item.item.use(game.player.fighter.inventory, game.player, game)
            turn = 'turn-used'
    return turn


def handle_drop(key, game, turn):
    if key.c is ord(game.keys.key_drop):
        chosen_item = inventory.inventory(game.dungeon_console, game.player, game)
        if chosen_item is not None:
            if chosen_item in game.player.fighter.inventory:
                chosen_item.objects = game.objects
                chosen_item.item.drop(game.player.fighter.inventory, game.player)
                chosen_item.send_to_back()
            turn = 'turn-used'
    return turn


def handle_stairs(key, game, turn):
    if chr(key.c) == '<':
        for object in game.objects:
            if object.x == game.player.x and object.y == game.player.y and object.misc:
                if object.misc.type == 'up':
                    if game.level.depth == 1:
                        game.go_to_town()

                        turn = 'turn-used'
                    else:
                        game.prev_level()

                        turn = 'turn-used'

    if chr(key.c) == '>':
        for object in game.objects:
            if object.x == game.player.x and object.y == game.player.y and object.misc:
                if object.misc.type == 'down':
                    game.new_level()
                    turn = 'turn-used'
    return turn


def handle_quit(key, game, turn):
    # return 'quit'
    if key.vk == libtcod.KEY_ESCAPE:
        message = 'Return to main menu?'
        w = len(message) * 2
        d_box = dialog_box.DialogBox(game, w, 10, 20, 20, message, type='option', con=game.dungeon_console)
        first = True
        while 1:
            confirm = d_box.display_box()
            if confirm == 1:
                d_box.destroy_box()
                game.ai_director.dump_data()
                return 'exit'  # exit game
            elif confirm == 0:
                if first:
                    first = False
                else:
                    d_box.destroy_box()
                    return 'didnt-take-turn'


def handle_help_screen(key, game, turn):
    if key.c is ord(game.keys.key_help):
        # help_mod = help_module.HelpModule(game.gEngine, game, 0, 0, 25, 7, "Help")
        # help_mod.setup()
        # game.gEngine.add_module(help_mod)
        game.gEngine.toggle_module(game.gEngine.get_module_by_name("HelpPopup"))
        pass
    return turn


def handle_esc_menu(key, game, turn):
    if key.vk == libtcod.KEY_ESCAPE and game.active:
        m = esc_menu.EscMenu(game.gEngine, game)
        game.gEngine.add_module(m)
        m.activate()


def handle_open(key, game, turn):
    if key.c is ord('o'):
        x = game.player.x
        y = game.player.y
        targets = check_next_to_player(game, x, y)
        if targets:
            for target in targets:
                if target.misc:
                    target.misc.activate(game.player)
                    return 'turn-used'
    return turn


def get_move_direction(key, game):
    move_keys = {game.keys.key_north: (0, -1),
                 game.keys.key_south: (0, 1),
                 game.keys.key_east: (1, 0),
                 game.keys.key_west: (-1, 0),
                 }
    px, py = move_keys[key]
    direction = ""
    if key == game.keys.key_north:
        direction = "north"
    if key == game.keys.key_south:
        direction = "south"
    if key == game.keys.key_east:
        direction = "east"
    if key == game.keys.key_west:
        direction = "west"
    return px, py, direction


def check_for_target(game, x, y):
    for object in game.objects: # TODO Refactor down to 1 line dummy
        if object.fighter and object.x == x and object.y == y:
            return object
        if object.npc and object.x == x and object.y == y:
            return object
        if object.misc and object.x == x and object.y == y:
            return object
    return None


def player_move_or_attack(game, dx, dy, direction=None):
    # the coordinates the player is moving to/attacking
    x = game.player.x + dx
    y = game.player.y + dy

    # try to find an attackable object there
    target = check_for_target(game, x, y)

    # attack if target found, move otherwise
    if target is not None:
        if target.fighter:
            game.player.fighter.attack(target, player=True, direction=direction, game=game)
            return 'turn-used'
        if target.npc:
            target.npc.activate(game.player, game)
            return 'turn-used'
        if target.blocks:
            target.misc.activate()
            return 'turn-used'
        else:
            return move_player(game, dx, dy)
    else:
        return move_player(game, dx, dy)

def check_stairs(target):
    if target.misc.type == "up":
        return True
    elif target.misc.type == "down":
        return True

def move_player(game, dx, dy):
    game.player.move(dx, dy, game.level.dungeon, game.objects)
    game.fov_recompute = True
    return 'player-moved'

def check_next_to_player(game, x, y):
    """
    Checks all surrounding cells for any object
    :param game: the main game instance
    :param x: player.x
    :param y: player.y
    :return: a list of targets, or None
    """
    targets = []
    for coord in close_coords:
        t = check_for_target(game, x+coord[0], y+coord[1])
        if t:
            targets.append(t)
    if len(targets) > 0:
        return targets
    else:
        return None

def pick_lock():
    pass

def bash_lock():
    pass