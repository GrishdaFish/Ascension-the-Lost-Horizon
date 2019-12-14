__author__ = 'Grishnak'
from gEngine.utilities.user_interface.button import *
from gEngine.utilities.user_interface.check_box import *
from gEngine.utilities.user_interface.menu import *
from gEngine.utilities.user_interface.dialog_box import *
from gEngine.utilities.user_interface.tab import *
import tcod as libtcod


def inventory(con, player, game, width=80, height=43):
    """
    TODO:
        Add in highlighting for Weapons and Equipment consoles
        Add in keyboard arrow selection support
        Add in "drop" mode, drop items from inventory
        Fix Weapons and Equipment keyboard handling
        Fix duplication bug when equipping items (fixed)
        Fix take off weapon confirmation when equipping an item (fixed)
        2 handed code needs work (?)
        keyboard input is sluggish. Might have to update libtcod to fix

    :param con: Destination console (not used atm)
    :param player: The main player object
    :param game: The main game object
    :param width: width of the inventory screen
    :param height: height of the inventory screen
    :return: An item that has been used (potion, scroll, etc..)
    """

    gear_list = player.fighter.gear.gimmie_da_armors() # REPLACING player.fighter.equipment


    equip_height = 14
    wield_height = 8
    compare_height = height - (equip_height - wield_height) - (wield_height * 2)

    r, g, b = libtcod.white
    equip_y = wield_height
    compare_y = equip_height + wield_height

    inventory_window = game.gEngine.console_new(width / 2, height)          ## TODO CONSIDER make helper function to reduce bloat
    game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
    game.gEngine.console_print_frame(inventory_window, 0, 0, width / 2, height, True)
    game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)

    equipment_window = game.gEngine.console_new(width / 2, equip_height)    ## TODO CONSIDER make helper function to reduce bloat
    game.gEngine.console_set_default_foreground(equipment_window, r, g, b)
    game.gEngine.console_print_frame(equipment_window, 0, 0, width / 2, equip_height, True)
    game.gEngine.console_set_default_background(equipment_window, 0, 0, 0)

    wielded_window = game.gEngine.console_new(width / 2, wield_height)      ## TODO CONSIDER make helper function to reduce bloat
    game.gEngine.console_set_default_foreground(wielded_window, r, g, b)
    game.gEngine.console_print_frame(wielded_window, 0, 0, width / 2, wield_height, True)
    game.gEngine.console_set_default_background(wielded_window, 0, 0, 0)

    compare_window = game.gEngine.console_new(width / 2, compare_height)    ## TODO CONSIDER make helper function to reduce bloat
    game.gEngine.console_set_default_foreground(compare_window, r, g, b)
    game.gEngine.console_print_frame(compare_window, 0, 0, width / 2, compare_height, True)
    game.gEngine.console_set_default_background(compare_window, 0, 0, 0)

    check_boxes = []
    slots = ['Torso    ',  # TODO DEPRECATE / REFACTOR all relations should be to gear_panel
             'Head     ',
             'Hands    ',
             'Legs     ',
             'Feet     ',
             'Arms     ',
             'Shoulders',
             'Back     ']
    # self.buttons.append(Button(self, self.option_labels[0], self.width//6-5, self.height/2-1, True))
    exit_button = Button(label='Exit', game=game, x_pos=(width / 2) - 9, y_pos=height - 6,
                         window=inventory_window, dest_x=width / 2, dest_y=0)
    drop_button = Button(label='Drop', game=game, x_pos=1, y_pos=height - 6,
                         window=inventory_window, dest_x=width / 2, dest_y=0)
    if len(player.fighter.inventory) == 0:
        inventory_items = ['Inventory is empty.']
    else:
        inventory_items = []
        for x in range(len(player.fighter.inventory)):
            check_boxes.append(CheckBox(x=1, y=x + 3))
            i = color_text(player.fighter.inventory[x].name.capitalize(), player.fighter.inventory[x].color)
            if player.fighter.inventory[x].item.check_stackable:
                i += ' (%d)' % player.fighter.inventory[x].item.qty
            elif player.fighter.inventory[x].item.equipment:
                if player.fighter.inventory[x].item.equipment.type == 'light_source':
                    i += ' (%d)' % player.fighter.inventory[x].item.equipment.fuel
            inventory_items.append(i)
    i_header = 'Inventory'
    i_header_size = len(i_header)
    i_header_pos = (width / 4) - (i_header_size / 2)

    w_header = 'Weapons'
    w_header_size = len(w_header)
    w_header_pos = (width / 8) - (w_header_size / 2)

    e_header = 'Equipment'
    e_header_size = len(e_header)
    e_header_pos = (width / 8) - (e_header_size / 2)

    c_header = 'Compare/Examine'
    c_header_size = len(c_header)
    c_header_pos = (width / 8) - (c_header_size / 2)

    return_item = None
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
    current_selection = 0
    master_check = CheckBox(1, 30, "Check/Uncheck All")

    #inventory_tab = Tab(parent=inventory, label="Inv.", x_pos=1, y_pos=1, game=game)

    while key.vk != libtcod.KEY_ESCAPE:

        game.gEngine.console_flush()
        # get input just after flush

        exit_input = exit_button.display()
        drop_input = drop_button.display()
        #inventory_tab.display()
        game.gEngine.console_blit(inventory_window, 0, 0, width / 2, height, 0, (width / 2), 0, 1.0, 1.0)
        game.gEngine.console_blit(wielded_window, 0, 0, width / 2, height, 0, 0, 0, 1.0, 1.0)
        game.gEngine.console_blit(equipment_window, 0, 0, width / 2, height, 0, 0, equip_y, 1.0, 1.0)
        game.gEngine.console_blit(compare_window, 0, 0, width / 2, height, 0, 0, compare_y, 1.0, 1.0)

        #game.gEngine.console_clear_all()
        #game.gEngine.console_clear(0)
        game.gEngine.console_clear(inventory_window)
        game.gEngine.console_clear(wielded_window)
        game.gEngine.console_clear(equipment_window)
        game.gEngine.console_clear(compare_window)
        key = libtcod.Key()
        mouse = libtcod.Mouse()
        libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)

        # set up draw screen
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(inventory_window, r, g, b)
        game.gEngine.console_print_frame(inventory_window, 0, 0, width / 2, height, True)

        game.gEngine.console_set_default_foreground(equipment_window, r, g, b)
        game.gEngine.console_print_frame(equipment_window, 0, 0, width / 2, equip_height, True)

        game.gEngine.console_set_default_foreground(wielded_window, r, g, b)
        game.gEngine.console_print_frame(wielded_window, 0, 0, width / 2, wield_height, True)

        game.gEngine.console_set_default_foreground(compare_window, r, g, b)
        game.gEngine.console_print_frame(compare_window, 0, 0, width / 2, compare_height, True)

        # ========================================================================
        # print inventory
        # ========================================================================
        game.gEngine.console_print(inventory_window, i_header_pos, 0, i_header)
        letter_index = ord('a')
        if len(player.fighter.inventory) > 0:
            y = 1
            for i in range(len(inventory_items)):
                text = '  (' + chr(letter_index) + ') ' + inventory_items[i]
                if current_selection == y - 1:
                    r, g, b = libtcod.color_lerp(player.fighter.inventory[i].color, libtcod.blue, 0.5)
                    game.gEngine.console_set_default_background(inventory_window, r, g, b)
                else:
                    game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
                game.gEngine.console_print_ex(inventory_window, 1, y + 2, libtcod.BKGND_SET, libtcod.LEFT, text)
                y += 1
                letter_index += 1
        game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
        game.gEngine.console_print(inventory_window, 1, 31,
                                   'Gold: ' + color_text(str(player.fighter.money), libtcod.gold))

        # ========================================================================
        # print equipped weapons
        # ========================================================================
        game.gEngine.console_print(wielded_window, w_header_pos, 0, w_header)
        index = ord('1')
        if player.fighter.gear.equipped['1h'] is None:
            text = '(' + chr(index) + ') ' + 'Main Hand : ' + color_text('Empty', libtcod.darker_gray)
        else:
            t = color_text(player.fighter.gear.equipped['1h'].name.capitalize(), player.fighter.gear.equipped['1h'].color)
            text = '(' + chr(index) + ') ' + 'Main Hand : ' + t
        index += 1
        game.gEngine.console_print(wielded_window, 1, 2, text)

        if player.fighter.gear.equipped['2h'] is None:
            text = '(' + chr(index) + ') ' + 'Off Hand: ' + color_text('Empty', libtcod.darker_gray)
        else:
            t = color_text(player.fighter.gear.equipped['2h'].name.capitalize(), player.fighter.gear.equipped['2h'].color)
            text = '(' + chr(index) + ') ' + 'Off Hand: ' + t
        index += 1
        game.gEngine.console_print(wielded_window, 1, 3, text)

        if player.fighter.gear.light_source is None:
            text = '(' + chr(index) + ') ' + 'Light Source : ' + color_text('Empty', libtcod.darker_gray)
        else:
            t = color_text(player.fighter.gear.light_source.name.capitalize(), player.fighter.gear.light_source.color)
            text = '(' + chr(index) + ') ' + 'Light Source: ' + t + " " + str(player.fighter.gear.light_source.item.equipment.fuel)
        index += 1
        game.gEngine.console_print(wielded_window, 1, 6, text)

        #if player.fighter
        item = player.fighter.gear.equipped['1h']
        if item:
            damage = '%dd%d+%d' % (
            item.item.equipment.damage[0], item.item.equipment.damage[1], item.item.equipment.damage[3])
            text = 'Damage   (total): ' + color_text(damage, libtcod.green)
            game.gEngine.console_print(wielded_window, 1, 4, text)
            accuracy = item.item.equipment.accuracy
            accuracy += game.player.fighter.get_skill(item.item.equipment.damage_type).get_bonus()
            text = 'Accuracy (total): ' + color_text(str(accuracy), libtcod.green)
            game.gEngine.console_print(wielded_window, 1, 5, text)

        # ========================================================================
        # print equipped armor
        # ========================================================================
        game.gEngine.console_print(equipment_window, e_header_pos, 0, e_header)
        i = 0
        game.gEngine.console_set_alignment(equipment_window, libtcod.LEFT)
        armor_bonus = 0
        armor_penalty = 0

        gear_slots = player.fighter.gear.gimmie_da_slots()
        for item in player.fighter.gear.gimmie_da_armors():      ## TODO REFACTOR / CONSIDER is this the bast way to accomplish
            text = '(' + chr(index) + ') ' + gear_slots[i] + ': '

            if item is None:
                text += color_text('Empty', libtcod.darker_gray)
            else:
                text += color_text(item.name.capitalize(), item.color)
                armor_bonus += item.item.equipment.bonus
                armor_penalty += item.item.equipment.penalty
            game.gEngine.console_print(equipment_window, 1, i + 2, text)
            i += 1
            index += 1
        c = color_text(str(armor_bonus), libtcod.green)
        text = 'Total Armor Bonus  :  ' + c
        game.gEngine.console_print(equipment_window, 1, i + 2, text)
        c = color_text(str(armor_penalty), libtcod.red)
        text = 'Total Armor Penalty: -' + c
        game.gEngine.console_print(equipment_window, 1, i + 3, text)
        game.gEngine.console_print(compare_window, c_header_pos, 0, c_header)

        # ========================================================================
        # handle mouse input
        # ========================================================================

        mc = master_check.update(mouse, width)
        master_check.render(inventory_window, game)
        if not mc:
            for box in check_boxes:
                box.update(mouse, width)
                box.render(inventory_window, game)
        else:
            for box in check_boxes:
                box.set_checked(master_check.get_checked())
                box.render(inventory_window, game)

        # Inventory input
        if width / 2 + 3 <= mouse.cx < width - 2:  # inventory screen dims
            if (mouse.cy - 3) < len(player.fighter.inventory) and mouse.cy - 3 >= 0:
                # if mouse.cy-3 <= len(player.fighter.inventory):
                item = player.fighter.inventory[mouse.cy - 3]
                current_selection = mouse.cy - 3
                if item.item.equipment:
                    game.gEngine.console_print(compare_window, 1, 2,
                                               'Name    : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print(compare_window, 1, 3,
                                               'Type    : ' + item.item.equipment.type.capitalize())

                    if item.item.equipment.type == 'melee':
                        damage = '%dd%d+%d' % (item.item.equipment.damage[0], item.item.equipment.damage[1],
                                               item.item.equipment.damage[3])
                        game.gEngine.console_print(compare_window, 1, 4, 'Damage  : ' + damage)
                        game.gEngine.console_print(compare_window, 1, 5,
                                                   'Accuracy: ' + str(item.item.equipment.accuracy))

                        game.gEngine.console_print(compare_window, 1, 7, 'Skill   : ' + item.item.equipment.damage_type)
                    elif item.item.equipment.type == 'light_source':
                        i = item.item.equipment.type.replace('_', ' ')
                        game.gEngine.console_print(compare_window, 1, 2,
                                                   'Name    : ' + color_text(item.name.capitalize(), item.color))
                        game.gEngine.console_print(compare_window, 1, 3,
                                                   'Type    : ' + i.capitalize())
                        game.gEngine.console_print(compare_window, 1, 4,
                                                   'Fuel    : ' + str(item.item.equipment.fuel))
                        game.gEngine.console_print(compare_window, 1, 5,
                                                   'Max Fuel: ' + str(item.item.equipment.max_fuel))
                    else:
                        game.gEngine.console_print(compare_window, 1, 4, 'Armor   : ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print(compare_window, 1, 5,
                                                   'Penalty : ' + str(item.item.equipment.penalty))
                        game.gEngine.console_print(compare_window, 1, 7,
                                                   'Location: ' + item.item.equipment.location.capitalize())
                    game.gEngine.console_print(compare_window, 1, 6, 'Value   : ' + str(item.item.value))
                    if item.item.equipment.effects is not None:  ## REFACTOR added to show gear effects
                        if len(item.item.equipment.effects) != 0:
                            show_effects(item, game, compare_window)

                if item.item.spell:
                    game.gEngine.console_print(compare_window, 1, 2,
                                               'Name  : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print(compare_window, 1, 3, 'Type  : ' + item.item.spell.type.capitalize())
                    game.gEngine.console_print(compare_window, 1, 4,
                                               'Power : ' + str(item.item.spell.min) + '-' + str(item.item.spell.max))
                    game.gEngine.console_print(compare_window, 1, 5, 'Range : ' + str(item.item.spell.range))
                    game.gEngine.console_print(compare_window, 1, 6, 'Radius: ' + str(item.item.spell.radius))
                    game.gEngine.console_print(compare_window, 1, 7, 'Value : ' + str(item.item.value))
                if mouse.lbutton and item.item.spell:
                    i_n = color_text(item.name.capitalize(), item.color)
                    message = 'Do you want to use %s?' % i_n
                    w = len(message) + 2
                    d_box = DialogBox(game, w, 10, width / 4, height / 2, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:  # make sure if the player uses a scroll or potion, we exit inventory
                        d_box.destroy_box()
                        # Remember to remove consoles in reverse order of creation to avoid OOB errors
                        return_item = item
                        break
                    else:
                        d_box.destroy_box()
                if mouse.lbutton and item.item.equipment:
                    if player.fighter.gear.light_source:
                        if player.fighter.gear.light_source.name == "magical light":
                            message = "You cannot remove this magical light!"
                            w = len(message) + 2
                            d_box = DialogBox(game, w, 10, width / 4, height / 2, message, con=inventory_window)
                            confirm = d_box.display_box()
                        else: ###### TODO FIX THE REPEATING LOGIC :)
                            i_n = color_text(item.name.capitalize(), item.color)
                            message = 'Do you want to put %s on?' % i_n
                            w = len(message) + 2
                            d_box = DialogBox(game, w, 10, width / 4, height / 2, message, type='option', con=inventory_window)
                            confirm = d_box.display_box()
                            if confirm == 1:
                                item.item.use(game.player.fighter.inventory, game.player, game)
                                d_box.destroy_box()
                                inventory_items = []
                                check_boxes = []
                                for x in range(len(player.fighter.inventory)):
                                    check_boxes.append(CheckBox(x=1, y=x + 3))
                                    i = color_text(player.fighter.inventory[x].name.capitalize(),
                                                   player.fighter.inventory[x].color)
                                    if player.fighter.inventory[x].item.check_stackable:
                                        i += ' (%d)' % player.fighter.inventory[x].item.qty
                                    inventory_items.append(i)
                    else:
                        i_n = color_text(item.name.capitalize(), item.color)
                        message = 'Do you want to put %s on?' % i_n
                        w = len(message) + 2
                        d_box = DialogBox(game, w, 10, width / 4, height / 2, message, type='option',
                                          con=inventory_window)
                        confirm = d_box.display_box()
                        if confirm == 1:
                            item.item.use(game.player.fighter.inventory, game.player, game)
                            d_box.destroy_box()
                            inventory_items = []
                            check_boxes = []
                            for x in range(len(player.fighter.inventory)):
                                check_boxes.append(CheckBox(x=1, y=x + 3))
                                i = color_text(player.fighter.inventory[x].name.capitalize(),
                                               player.fighter.inventory[x].color)
                                if player.fighter.inventory[x].item.check_stackable:
                                    i += ' (%d)' % player.fighter.inventory[x].item.qty
                                inventory_items.append(i)
            else:
                current_selection = None
        # game.gEngine.console_set_default_background(inventory_window, 0, 0, 0)
        # Wielded
        elif 0 <= mouse.cx <= ((width / 2) - 2):  # inventory screen dims
            if (mouse.cy - 2) < 2:  # wielded gone, magic #2 = # of hands(always)-old ver.=len(player.fighter.wielded)
                mouse_grabbed_index = mouse.cy - 2
                if mouse_grabbed_index == 0:
                    item =player.fighter.gear.equipped['1h']
                if mouse_grabbed_index == 1:
                    item = player.fighter.gear.equipped['2h']
                #item = player.fighter.wielded[mouse.cy - 2]
                if item is not None:
                    if item.item.equipment:
                        game.gEngine.console_print(compare_window, 1, 2,
                                                   'Name    : ' + color_text(item.name.capitalize(), item.color))
                        game.gEngine.console_print(compare_window, 1, 3,
                                                   'Type    : ' + item.item.equipment.type.capitalize())
                        damage = '%dd%d+%d' % (item.item.equipment.damage[0], item.item.equipment.damage[1],
                                               item.item.equipment.damage[3])
                        game.gEngine.console_print(compare_window, 1, 4,
                                                   'Damage  : ' + damage)
                        game.gEngine.console_print(compare_window, 1, 5,
                                                   'Accuracy: ' + str(item.item.equipment.accuracy))
                        game.gEngine.console_print(compare_window, 1, 6,
                                                   'Value   : ' + str(item.item.value))
                        if item.item.equipment.effects is not None: ## REFACTOR added to show gear effects
                            if len(item.item.equipment.effects) != 0:
                                show_effects(item, game, compare_window)
            # What in the son of a fuck is this about :-{>
            # elif (mouse.cy -2) > len(player.fighter.wielded)+1 and (mouse.cy -2 ) < len(player.fighter.wielded)+3 :
            # wielded no longer, exists so now its el magicka noir
            elif 1 > (mouse.cy) > 3:
                item = player.fighter.gear.light_source
                if item is not None:
                    i = item.item.equipment.type.replace('_', ' ')
                    game.gEngine.console_print(compare_window, 1, 2,
                                               'Name    : ' + color_text(item.name.capitalize(), item.color))
                    game.gEngine.console_print(compare_window, 1, 3,
                                               'Type    : ' + i.capitalize())
                    game.gEngine.console_print(compare_window, 1, 4,
                                               'Fuel    : ' + str(item.item.equipment.fuel))
                    game.gEngine.console_print(compare_window, 1, 5,
                                               'Max Fuel: ' + str(item.item.equipment.max_fuel))
                    if item.item.equipment.effects is not None: ## REFACTOR added to show gear effects
                        if len(item.item.equipment.effects) != 0:
                            show_effects(item, game, compare_window)
            # Equipment
            elif (mouse.cy - 2) - equip_y < len(gear_list):
                item = gear_list[mouse.cy - 2 - equip_y]
                if item is not None:
                    if item.item.equipment:
                        game.gEngine.console_print(compare_window, 1, 2,
                                                   'Name    : ' + color_text(item.name.capitalize(), item.color))
                        game.gEngine.console_print(compare_window, 1, 3,
                                                   'Type    : ' + item.item.equipment.type.capitalize())
                        game.gEngine.console_print(compare_window, 1, 4,
                                                   'Armor   : ' + str(item.item.equipment.bonus))
                        game.gEngine.console_print(compare_window, 1, 5,
                                                   'Penalty : ' + str(item.item.equipment.penalty))
                        game.gEngine.console_print(compare_window, 1, 6, 'Value   : ' + str(item.item.value))
                        if item.item.equipment.effects is not None: ## TODO REFACTOR added to show gear effects
                            if len(item.item.equipment.effects) != 0:
                                show_effects(item, game, compare_window)


            if mouse.lbutton and item is not None:
                i_n = color_text(item.name.capitalize(), item.color)
                if item.name == "magical light":
                    message = "You cannot remove this magical light!"
                    w = len(message) + 2
                    d_box = DialogBox(game,  w, 10, width/4, height/2, message, con=inventory_window)
                    confirm = d_box.display_box()
                else:
                    message = 'Do you want to take %s off?' % i_n
                    w = len(message) + 2
                    d_box = DialogBox(game, w, 10, width / 4, height / 2, message, type='option', con=inventory_window)
                    confirm = d_box.display_box()
                    if confirm == 1:
                        item.item.equipment.un_equip(game.player, item)
                        d_box.destroy_box()
                        inventory_items = []
                        check_boxes = []
                        if item.item.equipment.type == 'light_source':
                            player.fighter.gear.light_source = None
                        for x in range(len(player.fighter.inventory)):
                            check_boxes.append(CheckBox(x=1, y=x + 3))
                            i = color_text(player.fighter.inventory[x].name.capitalize(), player.fighter.inventory[x].color)
                            if player.fighter.inventory[x].item.check_stackable:
                                i += ' (%d)' % player.fighter.inventory[x].item.qty
                            if player.fighter.inventory[x].item.equipment:
                                if player.fighter.inventory[x].item.equipment.type == 'light_source':
                                    i += ' (%d)' % player.fighter.inventory[x].item.equipment.fuel
                            inventory_items.append(i)

                        for equipped_item in list(player.fighter.gear.equipped.values()):
                            if equipped_item == item:
                                player.fighter.gear.unquip_it(equipped_item)
                        #i = 0                                               #
                        #for x in player.fighter.wielded:                    #
                        #    if x == item:                                   #
                        #        player.fighter.wielded[i] = None            #
                        #    i += 1                                          #   TODO
                        #i = 0                                               #   REFACTOR ALL OF THIS
                        #for x in player.fighter.equipment:                  #
                        #    if x == item:                                   #
                        #        player.fighter.equipment[i] = None          #
                        #    i += 1                                          #

                        # for x in player.fighter.gear.equipped:            #
                        #    if x == item:                                  #   TO THIS, after full player refactor
                        #        player.fighter.gear.unquip_it(x)           #
        # keyboard input
        # keeps similar feel to old inventory if using the keys
        # keyboard input is sluggish as balls for some reason, need to look into it more
        index = key.c - ord('a')
        if key:
            if 0 <= index < len(inventory_items):
                return_item = player.fighter.inventory[index]
                break
            index = key.c - ord('1')
            if index == 0:
                return_item = player.figher.gear.gimmie_da_weapon()
                break
            elif index == 1:
                return_item = player.fighter.gear.gimmie_da_weapon(off_hand=True)
                break
            elif 2 <= index <= 10:
                gears = player.fighter.gear.gimmie_da_armors()
                return_item = gears[index - 2]
                break
            if key.vk == libtcod.KEY_DOWN:
                if current_selection is None:
                    current_selection = 0
                current_selection += 1
                if current_selection > len(inventory_items):
                    current_selection = 0
            if key.vk == libtcod.KEY_UP:
                if current_selection is None:
                    current_selection = 0
                current_selection -= 1
                if current_selection < 0:
                    current_selection = len(inventory_items)
        # ========================================================================
        # handle buttons
        # ========================================================================
        for i in drop_input:
            if i != -1:
                message = 'Drop all selected items?'
                w = len(message) + 2
                d_box = DialogBox(game, w, 10, width / 2 - w / 2, height / 2 - 5, message, type='option',
                                  con=inventory_window)
                confirm = d_box.display_box()
                if confirm == 1:
                    d_box.destroy_box()
                    master_check.set_checked(False)
                    items_to_drop = []
                    for box in check_boxes:
                        if box.get_checked():
                            items_to_drop.append(player.fighter.inventory[box.y - 3])
                    for item_to_drop in items_to_drop:
                        if item_to_drop:
                            item_to_drop.objects = game.objects
                            item_to_drop.item.drop(player.fighter.inventory, player, False)
                            item_to_drop.send_to_back()
                    check_boxes = []
                    inventory_items = []
                    for x in range(len(player.fighter.inventory)):
                        check_boxes.append(CheckBox(x=1, y=x + 3))
                        inventory_items.append(color_text(player.fighter.inventory[x].name.capitalize(),
                                                          player.fighter.inventory[x].color))
                else:
                    d_box.destroy_box()
        # ========================================================================
        # handle exit button
        # ========================================================================

        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break
    # Remember to remove consoles in reverse order of creation to avoid OOB errors
    drop_button.destroy_button()
    exit_button.destroy_button()
    game.gEngine.console_remove_console(compare_window)
    game.gEngine.console_remove_console(wielded_window)
    game.gEngine.console_remove_console(equipment_window)
    game.gEngine.console_remove_console(inventory_window)

    return return_item


def show_effects(item, game, compare_window):
    if item.item.equipment.effects is not None:
        if len(item.item.equipment.effects) != 0:
            game.gEngine.console_print_ex(compare_window, 1, 8, libtcod.BKGND_SET, libtcod.LEFT,
                                          'Effects : ')
            y = 8
            x = 11

            for fx in item.item.equipment.effects:
                effect_amount = color_text(fx.amount, game.player.fighter.stat.get_effect_color(fx))
                game.gEngine.console_print_ex(compare_window, x, y, libtcod.BKGND_SET, libtcod.LEFT,
                                              str(fx.effect_name) + " " + str(effect_amount) + " " + fx.effect_real_name)
                y += 1
