from gEngine.utilities.user_interface.button import *
from gEngine.utilities.user_interface.check_box import *
from gEngine.utilities.user_interface.menu import *
from gEngine.utilities.user_interface.dialog_box import *
from game.user_interface import inventory
from game.user_interface import shop
import tcod as libtcod
import os
import sys
from gEngine import gEngine as _gEngine

def equipment_menu(equipment ,screen_height ,screen_width ,game):
    slots = ['torso',
             'head',
             'hands',
             'legs',
             'feet',
             'arms',
             'shoulders',
             'back']

    options = []
    wielded = equipment[0]
    equip = equipment[1]
    acc = equipment[2]
    equip_option =[]

    if wielded[0]:
        item = 'Right hand:  ' +color_text(wielded[0].name ,wielded[0].color)
    else:
        item = 'Right hand: Empty'
    options.append(item)
    equip_option.append(wielded[0])
    if wielded[1]:
        item = 'Left hand:  ' +color_text(wielded[1].name ,wielded[1].color)
    else:
        item = 'Left hand: Empty'
    options.append(item)
    equip_option.append(wielded[1])

    for i in range(len(slots)):
        if not equip[i]:
            s =slots[i]
            item = s.capitalize() + ': Empty'
        else:
            s = slots[i].capitalize()
            item = s + ': ' + color_text(equip[i].name, equip[i].color)
        equip_option.append(equip[i])
        options.append(item)
    width = 6
    letter_index = ord('a')
    for item in options:
        if len(item) > width:
            width = len(item)

    width += 6
    height = 22
    window = game.gEngine.console_new(width, height)
    r, g, b = libtcod.white
    game.gEngine.console_set_default_foreground(window, r, g, b)
    game.gEngine.console_print_frame(window, 0, 0, width, height, True)  # ,'Equipment')
    # game.gEngine.console_hline(window,1,4,width-2)
    game.gEngine.console_print(window, width // 2, 4, 'Armor')

    for i in range(len(options)):
        if i < 2:
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window, 1, i + 1, text)
        else:
            text = '(' + chr(letter_index) + ') ' + options[i]
            game.gEngine.console_print(window, 1, i + 4, text)
        letter_index += 1

    x = screen_width / 2 - width / 2
    y = screen_height / 2 - height / 2

    game.gEngine.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    game.gEngine.console_flush()

    key = libtcod.console_wait_for_keypress(True)
    index = key.c - ord('a')
    if index >= 0 and index < len(options):
        if index < 2:  ##For Weapons
            if equip_option[index]:  ##If something is equipped on the slot, remove it
                msg = 'Take off ' + color_text(equip_option[index].name, equip_option[index].color) + ' ?'
                if confirm_screen(0, msg, screen_height, screen_width, game=game):
                    equip_option[index].item.equipment.un_equip(game.player, equip_option[index])
                    if equip_option[index].item.equipment.handed == 2:
                        if index == 0:
                            wielded[1] = None
                        else:
                            wielded[0] = None
                    wielded[index] = None

            else:  ##otherwise pop into the inventory, to select an item to equip
                msg = 'Please select a weapon to equip.'
                opt = []
                for item in game.player.fighter.inventory:  ##grab only weapons
                    if item.item.equipment:
                        if item.item.equipment.type == 'melee':
                            # item = color_text(item.name,item.color)
                            opt.append(item)
                chosen = inventory_menu(0, msg, opt, 50, screen_height, screen_width, game=game)
                if chosen:  ##if one was selected, confirm to equip it
                    if not isinstance(chosen, int):
                        msg = 'Put on ' + color_text(chosen.item.owner.name, chosen.item.owner.color) + ' ?'
                        if confirm_screen(0, msg, screen_height, screen_width, game=game):
                            chosen.item.use(game.player.fighter.inventory, game.player, game)

        else:  ##Armor, same procedure as weapons
            if equip_option[index]:
                msg = 'Take off ' + color_text(equip_option[index].name, equip_option[index].color) + ' ?'
                if confirm_screen(0, msg, screen_height, screen_width, game=game):
                    equip_option[index].item.equipment.un_equip(game.player, equip_option[index])
                    equip[index - 2] = None

            else:
                msg = 'Please select a piece of armor to equip.'
                opt = []
                for item in game.player.fighter.inventory:
                    if item.item.equipment:
                        if item.item.equipment.type == 'armor':
                            # item = color_text(item.name,item.color)
                            opt.append(item)
                chosen = inventory_menu(0, msg, opt, 50, screen_height, screen_width, game=game)
                if chosen:
                    if not isinstance(chosen, int):
                        msg = 'Put on ' + color_text(chosen.item.owner.name, chosen.item.owner.color) + ' ?'
                        if confirm_screen(0, msg, screen_height, screen_width, game=game):
                            chosen.item.use(game.player.fighter.inventory, game.player, game)

        game.gEngine.console_remove_console(window)
        return
    game.gEngine.console_remove_console(window)
    return


def inventory_menu(con, header, inventory, INVENTORY_WIDTH, SCREEN_HEIGHT,
                   SCREEN_WIDTH, is_name=False, game=None):
    # show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    elif not is_name:
        options = [color_text(item.name, item.color) for item in inventory]
    else:
        options = inventory
    index = menu(con, header, options, INVENTORY_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, game=game)
    # if an item was chosen, return it
    if index is None or len(inventory) == 0:
        return None
    if not is_name:
        return inventory[index]  # .item
    else:
        return index


def options_menu(con, header, options, screen_width, screen_height, bg=None):
    key_sets = []
    current_set = ''
    for option in options:
        if option.set_name:
            key_sets.append(option)
        if option.key_set:
            current_set = option.key_set


def help_menu():
    pass


def character_menu(con, header, skill_list, screen_width, screen_height, game, is_name=False):
    options = []
    if len(skill_list) == 0:
        options = ['No skills to display']
        length = len('No skills to display')
    else:
        length = 0
        for item in skill_list:
            skill = ''
            skill += item.get_name()
            skill += ' Level: ' + str(item.get_bonus())
            options.append(skill)
            l = len(skill)
            if l > length:
                length = l
    length += 2
    index = menu(con, header, options, length, screen_height, screen_width, bg=None, game=game)
    if index is None or len(skill_list) == 0:
        return None
    if not is_name:
        return skill_list[index]
    else:
        return index


def town_menu(con, header, game, width, screen_height, screen_width):
    options = ['The Helm and Buckler',
               "Johan's Weaporium",
               "Fizzilip's Magiteria",
               'Quests',
               'Finished', ]
    if _gEngine.RELEASE:
        path = getattr(sys, "_MEIPASS", ".")
    else:
        path = sys.path[0]
    path = os.path.join(path, 'content')
    path = path.replace('core.exe', '')
    backgrounds = [os.path.join(path, 'img', 'bg-arm.png'),
                   os.path.join(path, 'img', 'bg-wep.png'),
                   os.path.join(path, 'img', 'bg-magic.png'), ]
    container = []
    menus = []
    weapon, armor, consum, quest = [], [], [], []

    for i in range(10):  ##Need to init objects and message in object creation
        item = game.build_objects.build_equipment(game, 0, 0, 'melee')
        weapon.append(item)
        item = game.build_objects.build_equipment(game, 0, 0, 'armor')
        armor.append(item)
    for i in range(10):
        consume = game.build_objects.build_potion(game, 0, 0)
        consum.append(consume)
        consume = game.build_objects.build_scroll(game, 0, 0)
        consum.append(consume)

    container.append(armor)
    container.append(weapon)
    container.append(consum)
    container.append(quest)

    bg = os.path.join(path, 'img', 'bg-town.png')
    t_menu = Menus(game.gEngine, screen_height, screen_width, width, header, options, bg=bg)

    while 1:
        t_menu.is_visible = True
        libtcod.mouse_get_status()
        index = t_menu.run()
        if index == len(options) - 1 or index is None:
            t_menu.destroy_menu()
            break

        if index != (len(options) - 1) and index is not None and index != -1:
            t_menu.is_visible = False
            if index < (len(backgrounds)):
                item = shop.shop(0, game.player, game, container=container[index], bg=backgrounds[index],
                            header=options[index])
                # item=shop(con,options[index],game,width,
                #    screen_height,screen_width,container[index],backgrounds[index])
            else:
                item = shop.shop(0, game.player, game, container=container[index], header=options[index])
                # item=shop(con,options[index],game,width,
                #    screen_height,screen_width,container[index])
            if item is not None:
                container[index].pop(item)
            t_menu.last_input = 0
        libtcod.console_flush()
        game.gEngine.console_clear(0)



