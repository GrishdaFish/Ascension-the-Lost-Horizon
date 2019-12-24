__author__ = ['Grishnak', 'noobspanker']
import tcod as libtcod


def attack(attacker, direction, force_attack_target=None):
    # TODO need to add an attack type in the weapon that correlates to our attack patterns dict
    if force_attack_target:
        single_target(attacker, force_attack_target.fighter)
    else:
        targets = get_attack_pattern(attacker, direction)
        multi_target(attacker, targets)


def multi_target(attacker, targets):
    for target in targets:
        single_target(attacker, target.fighter)


def single_target(attacker, target):

    attack_roll = libtcod.random_get_int(0, 1, 20)
    attack_roll += get_accuracy_bonus(attacker)
    print("ATK ROLL= " + str(attack_roll))

    # Evasion chance always occurs, ends turn - no damage dealt
    if try_to_evade(target) > attack_roll:
        msg = attacker.owner.name.capitalize() + ' attacks ' + target.owner.name + ' but the attack was evaded!'

    # Parry chance is basically a second chance to evade
    elif target.gear.can_parry(target.gear.equipped['1h']) or \
            target.gear.can_parry(target.gear.equipped['2h']) and \
            try_to_parry(target) > attack_roll:
        msg = attacker.owner.name.capitalize() + ' attacks ' + target.owner.name + ' but the attack was deflected!'

    else:  # you hit, do some damage
        # TODO when weapon crits are added they will get checked at the same time as conditions:
        if attacker.stat.conditions:
            for fx in attacker.stat.conditions:
                print(attacker.owner.name + " trying to inflict: " + fx.effect_name)
                fx.inflict_condition(target)

        weapon_damage = attacker.gear.get_weapon_damage() - try_to_defend(target)
        if weapon_damage < 0:
            weapon_damage = 0

        elemental_damage = check_elemental_dam_res(attacker, target)
        if elemental_damage < 0:
            elemental_damage = 0

        # Block should not end turn, damage should only be mitigated in the range of the shield's equipment.damage
        mitigated_damage = 0
        if try_to_block(target) > attack_roll:
            mitigated_damage = get_blocked_amount(target)

        final_damage = weapon_damage + elemental_damage - mitigated_damage
        print("Damage" + str(final_damage))
        target.take_damage(final_damage, attacker.owner, attacker.game)
        msg = attacker.owner.name.capitalize() + ' attacks ' + target.owner.name + ' for ' + str(final_damage) + '!'

        attacker.gear.add_w_xp(100)

    if attacker.game:
        attacker.game.message.message(msg, 2)


def check_elemental_dam_res(attacker, target):
    final_damage = 0
    damages = attacker.stat.get_elem_array()
    resists = target.stat.get_elem_array(resist=True)
    for dmg in damages:
        final_damage += int(dmg)
        final_damage -= int(resists[damages.index(dmg)])
    return final_damage


def try_to_defend(target):
    defense = target.stat.get_stat("Defense")
    min_dam_mitigate = int(defense / 10)
    max_dam_mitigate = int(defense / 5)
    damage_mitigated = libtcod.random_get_int(0, min_dam_mitigate, max_dam_mitigate)
    return damage_mitigated


def try_to_block(creature):
    if creature.gear.equipped['2h'] is not None:
        if creature.gear.equipped['2h'].item.equipment.subtype == 'Shield':
            roll = libtcod.random_get_int(0, 1, 10)  # half of to hit roll
            roll += creature.stat.get_stat("Block")
            #roll += creature.fighter.stat.get_stat("Strength")
            #roll += creature.fighter.get_skill('Shield').get_bonus()
            #roll -= get_armor_penalty(creature) * 2
            return roll
    return 0


def get_blocked_amount(target):
    if target.gear.equipped['2h'] is not None and target.gear.is_shield(target.gear.equipped['2h']):
        shield = target.gear.gimmie_da_weapon(off_hand=True)
        return libtcod.random_get_int(0, shield.item.equipment.damage[0], shield.item.equipment.damage[1])
    return 0


def try_to_evade(target):
    # this can be a little fancier than this
    roll = libtcod.random_get_int(0, 1, 10)   # roll = 50% of atk roll
    roll += target.stat.get_stat("Evasion")
    return roll


def try_to_parry(creature):
    # previous incarnation added ((dex / 2) - 5) to roll and deducted armor_pen * 2
    parried = False
    hands = [creature.gear.equipped['1h'], creature.gear.equipped['2h']]
    roll = 0
    for each_weapon in hands:
        if creature.gear.can_parry(each_weapon):
            roll += creature.stat.get_stat("Parry")
            parried = True

    if parried:
        roll += libtcod.random_get_int(0, 1, 5)  # parry roll is getting a 75% handicap. parrying should be hard

    return roll


def get_accuracy_bonus(creature):
    roll = 0
    for weapon in [creature.gear.gimmie_da_weapon(), creature.gear.gimmie_da_weapon(off_hand=True)]:
        if weapon is not None:
            roll += weapon.item.equipment.accuracy

    return roll


# based on 0, 0 being player position
attack_patterns = {
        "partial cross": [(0, -1), (-1, -1,), (1, -1), (0, -2)],
        "checkered": [(-1, -1), (1, -1), (0, -2), (-1, -3), (1, -3)],
        " ": [(0, -1)],
        "": [(0, -1)],
        "default": [(0, -1)]
        # add additional north oriented attack patterns here
    }


def get_attack_pattern(attacker, direction, pattern="default"):
    """
    Returns direction normalized attack patterns
    :param direction: the cardinal direction of the attack
    :param pattern:  the requested pattern
    :return: the normalized array of attacks
    """
    # attacks = attack_patterns[pattern]
    # if not attacks:  # if we fail to get a proper attack pattern, we'll default to, well, "default"
    #    attacks = attack_patterns['default']
    target_locs = attack_patterns[pattern]
    altered_locs = []
    if direction == "north":
        for cell in target_locs:
            altered_locs.append(cell)
    elif direction == "south":
        for cell in target_locs:
            altered_locs.append((cell[0], -cell[1]))  # just negate the second value ( y direction)
        # return p
    elif direction == "east":
        for cell in target_locs:  # we may need to negate cell[0], need to test
            altered_locs.append((-cell[1], cell[0]))  # we swap the x and y then negate the new x
        # return attacks
    elif direction == "west":  # we may have to do some negating here, testing required
        for cell in target_locs:
            altered_locs.append((cell[1], cell[0]))  # we swap x and y directions
        # return attacks

    targets = []
    for target in altered_locs:
        if attacker.game.check_for_target(attacker.owner.x + target[0], attacker.owner.y + target[1]):
            targets.append(attacker.game.check_for_target(attacker.owner.x + target[0], attacker.owner.y + target[1]))

    print("attack pattern returning targets: " + str(targets))
    return targets

# # below is semi psuedocode implementation
# direction = "north"
# pattern = "default"
# attacks = calc_direction(direction, pattern)  # find your attack direction, and your weapons attack pattern
# for attack in attacks:  # loop for as many tiles as this weapon targets
#     target = check_for_target(attack)  # check for targets here, using the offsets
#     if target:
#         attack(target)
#
# # * *
# #  *
# # * *
# #  @

# def get_attack_pattern(weapon_type, direction):
#     targets = []
#
#     if weapon_type ==
#     return targets
#     """if direction and player:
#             t = None
#             if direction == "north" or direction == 'south':
#                 t = game.check_for_target(target.x + 1, target.y)
#                 if t:
#                     game.player.fighter.attack(t, player=True, game=game)
#                     t = None
#                 t = game.check_for_target(target.x - 1, target.y)
#                 if t:
#                     game.player.fighter.attack(t, player=True, game=game)
#             elif direction == "east" or direction == 'west':
#                 t = game.check_for_target(target.x, target.y + 1)
#                 if t:
#                     game.player.fighter.attack(t, player=True, game=game)
#                     t = None
#                 t = game.check_for_target(target.x - 1, target.y - 1)
#                 if t:
#                     game.player.fighter.attack(t, player=True, game=game)"""
#     # single target in front
#     # "Shield":
#     # "Short Sword": ['melee', 'Slash', True, True, 1, 0],
#     # "Long Sword": ['melee', 'Slash', False, False, 1, 0],
#     # "Hand Axe": ['melee', 'Slash', True, True, 1, 0],
#     # "Mace": ['melee', 'Smash', False, True, 1, 0],
#     # "Hammer": ['melee', 'Smash', False, True, 1, 0],
#     # "Staff": ['melee', 'Smash', False, False, 1, 0],
#     # "Dagger": ['melee', 'Stab', True, True, 1, 0],
#
#     # 3 targets in front
#     # "Great Sword": ['melee', 'Slash', False, False, 1, 0],
#
#     # alternating sides:
#     # "Battle Axe": ['melee', 'Slash', False, False, 1, 0],
#     # "Great Hammer": ['melee', 'Smash', False, False, 1, 0],
#     # "Flail": ['melee', 'Smash', False, False, 1, 0],
#
#     # 2 targets straight ahead
#     # "Polearm": ['melee', 'Stab', False, False, 1, 0],
#
#     # ranged
#     # "Throwing Axe": ['ranged', 'Slash', False, False, 1, 0],
#     # "Sling": ['ranged', 'Smash', False, True, 1, 0],
#     # "Bow": ['ranged', 'Stab', False, False, 1, 0],
#     # "Crossbow": ['ranged', 'Stab', False, True, 1, 0],
#     # "Throw Dagger": ['ranged', 'Stab', False, False, 1, 0],
#     # "Javelin": ['ranged', 'Stab', False, False, 1, 0],
