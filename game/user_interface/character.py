from gEngine.utilities import status_bar

__author__ = 'Grishnak'
from gEngine.utilities.user_interface.button import *
from gEngine.utilities.user_interface.check_box import *
from gEngine.utilities.user_interface.menu import *
from gEngine.utilities.user_interface.dialog_box import *
import tcod as libtcod


def get_centered_text(text, width):
    head = text
    s = len(head)
    pos = width - s/2
    return head, pos

def character_info(con, width, height, game, x=0, y=0):
    skill_window = game.gEngine.console_new(width/2, height)
    skill_window_y_pos = width/2
    s_header, s_pos = get_centered_text("Weapon Skill", width/4)

    char_window = game.gEngine.console_new(width/2, height/2)
    c_header, c_pos = get_centered_text(("%s's Skills and Abilities" % game.player.name), width/4)

    skill_desc_window = game.gEngine.console_new(width/2, height/2)
    skill_desc_pos = height/2
    d_header, d_pos = get_centered_text("Status Effects", width/4)

    exit_button = Button(label='Exit', game=game, x_pos=(width/2)-9, y_pos=height-6,
                         window=skill_window, dest_x=width/2, dest_y=0)
    current_selection = 0
    key = libtcod.console_check_for_keypress()
    first_print = True
    while key.vk != libtcod.KEY_ESCAPE:
        game.gEngine.console_flush()
        # get input just after flush
        # key = libtcod.Key()
        # mouse = libtcod.Mouse()
        # libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
        key, mouse = game.gEngine.handle_input()
        exit_input = exit_button.display()

        game.gEngine.console_blit(char_window, 0, 0, width/2, height/2, 0, 0, 0, 1.0, 1.0)
        game.gEngine.console_blit(skill_window, 0, 0, width/2, height, 0, skill_window_y_pos, 0, 1.0, 1.0)
        game.gEngine.console_blit(skill_desc_window, 0, 0, width/2, height/2, 0, 0, skill_desc_pos, 1.0, 1.0)

        game.gEngine.console_clear(char_window)
        game.gEngine.console_clear(skill_desc_window)
        game.gEngine.console_clear(skill_window)

        #Draw Character info
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(char_window, r, g, b)
        game.gEngine.console_print_frame(char_window, 0, 0, width/2, height/2, True)
        game.gEngine.console_print(char_window, c_pos, 0, c_header)
        game.gEngine.console_print(char_window, 1, 1, 'Name: %s' % game.player.name)

        player_hp_bar = status_bar.StatusBar(game.player.fighter, int(width/2)-10, libtcod.light_red,
                                                  libtcod.darker_red, char_window, type='hp', gEngine=game.gEngine)
        player_hp_bar.render(1, 2, game.gEngine)
        game.gEngine.console_set_alignment(player_hp_bar.con, int(libtcod.LEFT))
        game.gEngine.console_print(char_window, 1, 3, 'Level: %d' % game.player.fighter.level)
        player_xp_bar = status_bar.StatusBar(game.player.fighter, int(width/2)-10, libtcod.light_grey,
                                                  libtcod.dark_grey, char_window, type='xp', gEngine=game.gEngine)
        player_xp_bar.render(1, 4, game.gEngine)
        game.gEngine.console_set_alignment(player_xp_bar.con, int(libtcod.LEFT))

        s = color_text(str(game.player.fighter.stat.get_stat_base("Strength")), libtcod.light_gray)
        d = color_text(str(game.player.fighter.stat.get_stat_base("Dexterity")), libtcod.light_gray)
        i = color_text(str(game.player.fighter.stat.get_stat_base("Intelligence")), libtcod.light_gray)
        c = color_text(str(game.player.fighter.stat.get_stat_base("Constitution")), libtcod.light_gray)
        game.gEngine.console_print(char_window, 1, 7, 'Stats: Str [%s], Dex [%s]' % (s, d))
        game.gEngine.console_print(char_window, 1, 8, '       Int [%s], Con [%s]' % (i, c))

        hit_bonus = color_text(str(game.player.fighter.stat.get_stat("Accuracy")), libtcod.green)
        game.gEngine.console_print(char_window, 1, 10, 'Bonus to Hit  : [%s] ' % hit_bonus)

        bonus = color_text(str(game.player.fighter.stat.get_stat_mod("Defense")), libtcod.green)
        # bonus2 = color_text('10 +%d' % game.player.fighter.stat.get_stat("Defense"), libtcod.green)
        game.gEngine.console_print(char_window, 1, 11, 'Armor Rating  : [%s] ' % (bonus))

        block = color_text(str(game.player.fighter.stat.get_stat("Block")), libtcod.green)
        game.gEngine.console_print(char_window, 1, 12, 'Bonus to Block: [%s] ' % block)
        parry = color_text(str(game.player.fighter.stat.get_stat("Parry")), libtcod.green)
        game.gEngine.console_print(char_window, 1, 13, 'Parry chance  : [%s] ' % parry)

        penalty = color_text(str(game.player.fighter.stat.get_stat_pen("Evasion")), libtcod.red)
        # penalty2 = color_text('1d20 -%d' % game.player.fighter.stat.get_stat("Evasion"), libtcod.red)
        game.gEngine.console_print(char_window, 1, 14, 'Evasion Rating: [%s]' % (penalty))

        speed = color_text(str(game.player.fighter.stat.get_stat("Speed")), libtcod.light_gray)
        game.gEngine.console_print(char_window, 1, 16, 'Turn Speed: [%s]' % speed)

        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(skill_window, r, g, b)
        game.gEngine.console_print_frame(skill_window, 0, 0, width/2, height, True)
        game.gEngine.console_print(skill_window, s_pos, 0, s_header)
        t, p = get_centered_text('Type: Level / EXP / TNL', width/4)
        game.gEngine.console_print(skill_window, p, 1, t)
        y = 2
        for weapon_type in game.player.fighter.gear.weapon_panel.keys():
            level = game.player.fighter.gear.get_w_lvl(weapon_type)
            w_xp = game.player.fighter.gear.get_w_xp(weapon_type)
            w_xp_tnl = game.player.fighter.gear.get_w_xptnl(weapon_type)
            y = do_string_output(game, skill_window, y, "Lvl:%s " % str(level).ljust(2))
            bar = status_bar.StatusBar(game.player.fighter, int(width / 2) - 17, libtcod.light_red,
                                                 libtcod.darker_red, skill_window, type='hp', gEngine=game.gEngine)
            bar.render(14, y - 1, game.gEngine, [w_xp, w_xp_tnl], weapon_type)
            game.gEngine.console_set_alignment(bar.con, int(libtcod.LEFT))
            #y += 1
        ###########################################################################
        # y = 3
        # prepare a big dumb ass string to output ######################################################################
        #y = do_string_output(game, skill_window, y, " Stats:        Cur / Mod / Pen:")
        # format modifiers
        #mod_start_index = y
        #for fx_name in game.player.fighter.stat.panel['modifiers']:
        #    if fx_name != 'key':
        #        mod = game.player.fighter.stat.get_stat_mod(fx_name)
        #        pen = game.player.fighter.stat.get_stat_pen(fx_name)
        #        cur = game.player.fighter.stat.get_stat_base(fx_name) + mod - pen
        #        y = do_string_output(game, skill_window, y, "%s:  %s / %s / %d" %
        #                             (fx_name.ljust(12), str(cur).ljust(3), str(mod).ljust(3), pen))

        y += 1 ################################################################################################
        y = do_string_output(game, skill_window, y, " Elemental Effects:")
        y = do_string_output(game, skill_window, y, "Effect: Damage / Resist")
        # format combat effects
        combat_start_index = y
        for stat, val in zip(game.player.fighter.stat.panel['elemental'].keys(),
                             game.player.fighter.stat.panel['elemental'].values()):
            if stat != 'key':
                stat = color_text(str(stat), val[2])
                y = do_string_output(game, skill_window, y,
                                     "%s:  %s /    %d" % (stat.ljust(12), str(val[0]).ljust(4), val[1]))

        y += 1
        y = do_string_output(game, skill_window, y, " Conditions:")
        y = do_string_output(game, skill_window, y, "Effect: Damage / Resist / Trigger%")
        # format conditions
        conditions_start_index = y
        for stat, val in zip(game.player.fighter.stat.panel['conditions'].keys(),
                             game.player.fighter.stat.panel['conditions'].values()):
            if stat != 'key':
                stat = color_text(str(stat), val[3])
                y = do_string_output(game, skill_window, y, "%s:  %s /   %s /   %d " % (
                stat.ljust(12), str(val[0]).ljust(4), str(val[1]).ljust(4), val[2]))
        ################################################################################################################
        game.gEngine.console_set_default_background(skill_window, 0, 0, 0)

        game.gEngine.console_print_ex(skill_window, 1, y, libtcod.BKGND_SET, libtcod.LEFT, '')
        #    y += 1
        #    letter_index += 1
        game.gEngine.console_set_default_background(skill_window, 0, 0, 0)

        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(skill_desc_window, r, g, b)
        game.gEngine.console_print_frame(skill_desc_window, 0, 0, width / 2, height / 2, True)
        game.gEngine.console_print(skill_desc_window, d_pos, 0, d_header)
        # TODO THIS STUFF BELOW SHOULD USE HOVER DESCRIPTION
        # mouse input
        # stat = ""
        # sources = []
        # details = []

        # mod_count = game.player.fighter.stat.get_category_count('modifiers') + 3
        # combat_count = game.player.fighter.stat.get_category_count('elemental') + mod_count + 3
        # conditions_count = game.player.fighter.stat.get_category_count('conditions') + combat_count + 3
        #
        # if mouse.cx >= width / 2 + 3:
        #     if mod_count >= mouse.cy >= mod_start_index:
        #         current_mod_index = mod_start_index - 1  # offset by 1 because 1st index is key
        #         for stat_iter in game.player.fighter.stat.panel['modifiers']:
        #             if current_mod_index == mouse.cy:
        #                 stat = stat_iter
        #                 for things in game.player.fighter.stat.modifiers:
        #                     if things.effect_name == stat:
        #                         sources.append(things.item.owner.name)
        #                         details.append(str(things.amount) + " " + things.effect_real_name)
        #             current_mod_index += 1
        #     if combat_count >= mouse.cy >= combat_start_index:
        #         current_mod_index = combat_start_index - 1  # offset by 1 because 1st index is key
        #         for stat_iter in game.player.fighter.stat.panel['elemental']:
        #             if current_mod_index == mouse.cy:
        #                 if stat_iter != 'key':
        #                     stat = color_text(stat_iter, game.player.fighter.stat.panel['elemental'][stat_iter][2])
        #                     for things in game.player.fighter.stat.elemental_effects:
        #                         if things.effect_name == stat_iter:
        #                             sources.append(things.item.owner.name)
        #                             details.append(str(things.amount) + " " + things.effect_real_name)
        #             current_mod_index += 1
        #     if conditions_count >= mouse.cy >= conditions_start_index:
        #         current_mod_index = conditions_start_index - 1  # offset by 1 because 1st index is key
        #         for stat_iter in game.player.fighter.stat.panel['conditions']:
        #             if current_mod_index == mouse.cy:
        #                 if stat_iter != 'key':
        #                     stat = color_text(stat_iter, game.player.fighter.stat.panel['conditions'][stat_iter][3])
        #                     for things in game.player.fighter.stat.conditions:
        #                         if things.effect_name == stat_iter:
        #                             sources.append(things.item.owner.name)
        #                             details.append(str(things.amount) + " " + things.effect_real_name)
        #             current_mod_index += 1

        #            if mouse.cy-2 < len(game.player.fighter.stats) and mouse.cy >= 0:
        #                current_selection = mouse.cy-2
        #                stat = game.player.fighter.stat_panel[current_selection]
        #                desc = color_text(stat.get_description(), libtcod.light_gray)
        #                desc = "Stat Description: %s" % desc
        #                cat = color_text(stat.get_category(), libtcod.light_gray)
        #                cat = "Stat Category   : %s" % cat
        #                bonus = stat.get_bonus()
        #                name = stat.get_name()
        #                if bonus == stat_max:
        #                    bonus = color_text(str(bonus), libtcod.green)
        #                    name = color_text(name, libtcod.green)
        #                elif stat_max > bonus > 0:
        #                    bonus = color_text(str(bonus), libtcod.lighter_gray)
        #                    name = color_text(name, libtcod.lighter_gray)
        #                elif bonus == 0:
        #                    bonus = color_text(str(bonus), libtcod.dark_gray)
        #                    name = color_text(name, libtcod.dark_gray)
        #                else:
        #                    bonus = color_text(str(bonus), libtcod.red)
        #                    name = color_text(name, libtcod.red)
        #                if stat.get_category() == 'Discipline':
        #                    bonus = 'Increases your (%s) to-hit rolls by [%s].' % (name, bonus)
        #                elif stat.get_category() == 'Weapon':
        #                    bonus = 'Increases your (%s) damage by [%s].' % (name, bonus)

        #game.gEngine.console_print_rect(skill_desc_window, 1, 1, width / 2 - 2, 3, stat)
        #y = int(height / 2 + 1)

        if game.player.fighter.stat.active_conditions:
            y = 1
            if first_print:
                print(game.player.fighter.stat.active_conditions)
                first_print = False
            for condition in game.player.fighter.stat.active_conditions:
                if condition.duration > 0:
                    bar = status_bar.StatusBar(game.player.fighter, int(width / 2) - 17, condition.get_color(),
                                               libtcod.darker_red, skill_desc_window, type='hp', gEngine=game.gEngine)
                    bar.render(1, y, game.gEngine, [condition.duration, condition.total_duration], condition.effect_name)
                    game.gEngine.console_set_alignment(bar.con, int(libtcod.LEFT))
                    y += 1

                # player_stat_bar = status_bar.StatusBar(game.player.fighter, int(width / 2) - 10, condition.get_color(),
                #                                      condition.get_color(), skill_desc_window, type='xp', gEngine=game.gEngine)
                # player_stat_bar.render(1, y, game.gEngine, [condition.duration, condition.total_duration], condition.effect_name)
                # game.gEngine.console_set_alignment(player_stat_bar.con, int(libtcod.LEFT))
                # y += 1
                #
                # line = '%s ' % condition.effect_name
                # y = do_string_output(game, skill_desc_window, y, line)
                # y += 1
        # for source, detail in zip(sources, details):
        #     game.gEngine.console_print(skill_desc_window, 1, y, "%s: + %s" % (source, detail))
        #     y += 1
        #
        r, g, b = libtcod.white
        # game.gEngine.console_set_default_foreground(skill_desc_window, r, g, b)
        # game.gEngine.console_print_frame(skill_desc_window, 0, 0, width/2, height/2, True)
        # game.gEngine.console_print(skill_desc_window, d_pos, 0, d_header)

        #game.gEngine.console_print_rect(skill_desc_window, 1, 1, width/2-2, 3, "desc")
        #game.gEngine.console_print(skill_desc_window, 1, 5, "cat")
        #game.gEngine.console_print_rect(skill_desc_window, 1, 7, width/2-2, 3, bonus)
        if mouse.lbutton_pressed:
            game.player.fighter.apply_skill_points(game.player.fighter.skills[current_selection]) # use unused player skill points

        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break

    exit_button.destroy_button()
    game.gEngine.console_remove_console(skill_desc_window)
    game.gEngine.console_remove_console(char_window)
    game.gEngine.console_remove_console(skill_window)

    return None

def stat_panel_info(con, width, height, game, x=0, y=0):
    stat_window = game.gEngine.console_new(width/2, height)
    stat_window_y_pos = width/2
    s_header, s_pos = get_centered_text("Stats and Modifiers", width/4)

    condition_window = game.gEngine.console_new(width/2, height/2)
    c_header, c_pos = get_centered_text(("%s's Conditions" % game.player.name), width/4)

    stat_desc_window = game.gEngine.console_new(width/2, height/2)
    stat_desc_pos = height/2
    d_header, d_pos = get_centered_text("Description", width/4)

    exit_button = Button(label='Exit', game=game, x_pos=(width/2)-9, y_pos=height-6,
                         window=stat_window, dest_x=width/2, dest_y=0)
    current_selection = 0
    key = libtcod.console_check_for_keypress()
    while key.vk != libtcod.KEY_ESCAPE:
        game.gEngine.console_flush()
        # get input just after flush
        # key = libtcod.Key()
        # mouse = libtcod.Mouse()
        # libtcod.sys_check_for_event(libtcod.EVENT_MOUSE | libtcod.EVENT_KEY_PRESS, key, mouse)
        key, mouse = game.gEngine.handle_input()
        exit_input = exit_button.display()

        game.gEngine.console_blit(condition_window, 0, 0, width/2, height/2, 0, 0, 0, 1.0, 1.0)
        game.gEngine.console_blit(stat_window, 0, 0, width/2, height, 0, stat_window_y_pos, 0, 1.0, 1.0)
        game.gEngine.console_blit(stat_desc_window, 0, 0, width/2, height/2, 0, 0, stat_desc_pos, 1.0, 1.0)

        game.gEngine.console_clear(condition_window)
        game.gEngine.console_clear(stat_desc_window)
        game.gEngine.console_clear(stat_window)

        #Draw Character info
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(condition_window, r, g, b)
        game.gEngine.console_print_frame(condition_window, 0, 0, width/2, height/2, True)
        game.gEngine.console_print(condition_window, c_pos, 0, c_header)
        # game.gEngine.console_print(condition_window, 1, 1, 'Name: %s' % game.player.name)
        #############################################################################################################
        # line_ind = 1
        # for condition in game.player.fighter.stat.active_conditions:
        #     name = condition.effect_name
        #     amount = condition.amount
        #     duration = condition.duration
        #     stat = condition.stat_effect
        #     game.gEngine.console_print(condition_window, 1, line_ind, '%s %s %s %s' % name, stat, amount, duration)
        #     line_ind += 1
        #############################################################################################################
        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(stat_window, r, g, b)
        game.gEngine.console_print_frame(stat_window, 0, 0, width/2, height, True)
        game.gEngine.console_print(stat_window, s_pos, 0, s_header)
        t, p = get_centered_text('Damage / Resistance:', width/4)
        game.gEngine.console_print(stat_window, p, 1, t)

        y = 3
        # prepare a big dumb ass string to output ######################################################################
        y = do_string_output(game, stat_window, y, " Stats:        Cur / Mod / Pen:")
        # format modifiers
        mod_start_index = y
        for fx_name in game.player.fighter.stat.panel['modifiers']:
            if fx_name != 'key':
                mod = game.player.fighter.stat.get_stat_mod(fx_name)
                pen = game.player.fighter.stat.get_stat_pen(fx_name)
                cur = game.player.fighter.stat.get_stat_base(fx_name) + mod - pen
                y = do_string_output(game, stat_window, y, "%s:  %s / %s / %d" %
                                 (fx_name.ljust(12), str(cur).ljust(3), str(mod).ljust(3), pen))

        y += 1
        y = do_string_output(game, stat_window, y, " Elemental Effects:")
        y = do_string_output(game, stat_window, y, "Effect: Damage / Resist")
        # format combat effects
        combat_start_index = y
        for stat, val in zip(game.player.fighter.stat.panel['elemental'].keys(),
                             game.player.fighter.stat.panel['elemental'].values()):
            if stat != 'key':
                stat = color_text(str(stat), val[2])
                y = do_string_output(game, stat_window, y, "%s:  %s /    %d" % (stat.ljust(12), str(val[0]).ljust(4), val[1]))

        y += 1
        y = do_string_output(game, stat_window, y, " Conditions:")
        y = do_string_output(game, stat_window, y, "Effect: Damage / Resist / Trigger%")
        # format conditions
        conditions_start_index = y
        for stat, val in zip(game.player.fighter.stat.panel['conditions'].keys(),
                             game.player.fighter.stat.panel['conditions'].values()):
            if stat != 'key':
                stat = color_text(str(stat), val[3])
                y = do_string_output(game, stat_window, y, "%s:  %s /   %s /   %d " % (stat.ljust(12), str(val[0]).ljust(4), str(val[1]).ljust(4), val[2]))
        ################################################################################################################
        game.gEngine.console_set_default_background(stat_window, 0, 0, 0)

        game.gEngine.console_print_ex(stat_window, 1, y,libtcod.BKGND_SET, libtcod.LEFT, '')
        #    y += 1
        #    letter_index += 1
        game.gEngine.console_set_default_background(stat_window, 0, 0, 0)

        r, g, b = libtcod.white
        game.gEngine.console_set_default_foreground(stat_desc_window, r, g, b)
        game.gEngine.console_print_frame(stat_desc_window, 0, 0, width/2, height/2, True)
        game.gEngine.console_print(stat_desc_window, d_pos, 0, d_header)

        #mouse input
        stat = ""
        sources = []
        details = []

        mod_count = game.player.fighter.stat.get_category_count('modifiers') + 3
        combat_count = game.player.fighter.stat.get_category_count('elemental') + mod_count + 3
        conditions_count = game.player.fighter.stat.get_category_count('conditions') + combat_count + 3

        if mouse.cx >= width/2 +3:
            if mod_count >= mouse.cy >= mod_start_index:
                current_mod_index = mod_start_index - 1 # offset by 1 because 1st index is key
                for stat_iter in game.player.fighter.stat.panel['modifiers']:
                    if current_mod_index == mouse.cy:
                        stat = stat_iter
                        for things in game.player.fighter.stat.modifiers:
                            if things.effect_name == stat:
                                sources.append(things.item.owner.name)
                                details.append(str(things.amount) + " " + things.effect_real_name)
                    current_mod_index += 1
            if combat_count >= mouse.cy >= combat_start_index:
                current_mod_index = combat_start_index - 1  # offset by 1 because 1st index is key
                for stat_iter in game.player.fighter.stat.panel['elemental']:
                    if current_mod_index == mouse.cy:
                        if stat_iter != 'key':
                            stat = color_text(stat_iter, game.player.fighter.stat.panel['elemental'][stat_iter][2])
                            for things in game.player.fighter.stat.elemental_effects:
                                if things.effect_name == stat_iter:
                                    sources.append(things.item.owner.name)
                                    details.append(str(things.amount) + " " + things.effect_real_name)
                    current_mod_index += 1
            if conditions_count >= mouse.cy >= conditions_start_index:
                current_mod_index = conditions_start_index - 1 # offset by 1 because 1st index is key
                for stat_iter in game.player.fighter.stat.panel['conditions']:
                    if current_mod_index == mouse.cy:
                        if stat_iter != 'key':
                            stat = color_text(stat_iter, game.player.fighter.stat.panel['conditions'][stat_iter][3])
                            for things in game.player.fighter.stat.conditions:
                                if things.effect_name == stat_iter:
                                    sources.append(things.item.owner.name)
                                    details.append(str(things.amount) + " " + things.effect_real_name)
                    current_mod_index += 1

#            if mouse.cy-2 < len(game.player.fighter.stats) and mouse.cy >= 0:
#                current_selection = mouse.cy-2
#                stat = game.player.fighter.stat_panel[current_selection]
#                desc = color_text(stat.get_description(), libtcod.light_gray)
#                desc = "Stat Description: %s" % desc
#                cat = color_text(stat.get_category(), libtcod.light_gray)
#                cat = "Stat Category   : %s" % cat
#                bonus = stat.get_bonus()
#                name = stat.get_name()
#                if bonus == stat_max:
#                    bonus = color_text(str(bonus), libtcod.green)
#                    name = color_text(name, libtcod.green)
#                elif stat_max > bonus > 0:
#                    bonus = color_text(str(bonus), libtcod.lighter_gray)
#                    name = color_text(name, libtcod.lighter_gray)
#                elif bonus == 0:
#                    bonus = color_text(str(bonus), libtcod.dark_gray)
#                    name = color_text(name, libtcod.dark_gray)
#                else:
#                    bonus = color_text(str(bonus), libtcod.red)
#                    name = color_text(name, libtcod.red)
#                if stat.get_category() == 'Discipline':
#                    bonus = 'Increases your (%s) to-hit rolls by [%s].' % (name, bonus)
#                elif stat.get_category() == 'Weapon':
#                    bonus = 'Increases your (%s) damage by [%s].' % (name, bonus)

        game.gEngine.console_print_rect(stat_desc_window, 1, 1, width/2-2, 3, stat)
        y = 5
        for source, detail in zip(sources, details):
            game.gEngine.console_print(stat_desc_window, 1, y, "%s: + %s" % (source, detail))
            y += 1
        #game.gEngine.console_print_rect(stat_desc_window, 1, 7, width/2-2, 3, detail)

            #    if mouse.lbutton_pressed:
            #        game.player.fighter.apply_skill_points(game.player.fighter.skills[current_selection]) # use unused player skill points

        for i in exit_input:
            if i != -1:
                key.vk = libtcod.KEY_ESCAPE
                break

    exit_button.destroy_button()
    game.gEngine.console_remove_console(stat_desc_window)
    game.gEngine.console_remove_console(condition_window)
    game.gEngine.console_remove_console(stat_window)

    return None

def do_string_output(game, stat_window, y, line):
    game.gEngine.console_print(stat_window, 2, y, line)
    y += 1
    return y

