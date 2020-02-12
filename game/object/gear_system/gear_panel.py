from game.object.gear_system.modifier_template import DamageType

__author__ = 'noobspanker'
import tcod as libtcod

"""
[["armor"]]
    name = "plate helm"
    cell = '^'
    type = "armor"
    location = "head"
    base_value = 50
    description = "Low visibility"
    threat_level = 0.5
    allowed_materials = 3 #1 for cloth, 2 for metal, 3 for both
    bonus = 1
    penalty = 1

[["weapon"]]
    name="great sword"  ------ in game name, not relevant here
    cell='/' #should keep weapons this character
#    type="melee" -------------------------------------------------------DICTATED BY REAL WEAPON TYPE #CHANGING  REAL VALUES TO bow, dagger, mace...
#    handed=2  #how many hands it takes to wield
-    dual_wield=false  #can be dual wielded? ----------------------------DICTATED BY REAL WEAPON TYPE + CHAR PERKS #deletable
#-    damage_type="Straightsword"  #2x damage vs this protection type ---- 3 types now - DICTATED BY REAL WEAPON TYPE slash, smash, stab
-    family = "straightsword" # the skill family this weapon belongs in - SAME AS ABOVE #deletable
    base_value=100  #base value of the item before materials ----------- different system, dont matter here could be the same for all base weapons
    description=""  #Description of the item, not including material --- different system, dont matter here
    threat_level=0.5  #for calculating spawns, higher number = more dangerous - relevant to threat generator
    size="tiny"     -------------------------imp. loc. Under consideration
#    damage = [2, 10, 1, 0] # min damage, max damage, mutliplier, bonus (2d10*1+0)
#    accuracy = 0 # accuracy bonus or penalty
"""

class WeaponType:
    """ maintain personal upgrade and base details about weapon usage """
    def __init__(self, owner, name, combat_type, damage_type, can_dual, can_shield, can_parry, handed_override):
        self.owner = owner
        self.name = name
        self.level = 1
        self.xp = 0
        self.combat_type = combat_type  # melee / ranged
        self.damage_type = damage_type  # shield / slash / smash / stab
        self.can_dual = can_dual
        self.can_shield = can_shield
        self.can_parry = can_parry
        self.handed_override = handed_override
        # self.perk_tree = owner.perks.get_tree(self.name)

class GearPanel:
    """ Will hold and manage all aspects of gear equipped on a figher """

    def __init__(self, owner):
        self.owner = owner
        self.light_source = None

        self.damage_types = {
            'Shield': DamageType('Shield', self.owner),
            'Slash':  DamageType('Slash', self.owner),
            'Smash':  DamageType('Smash', self.owner),
            'Stab':   DamageType('Stab', self.owner)
        }

        self.weapon_panel = {  # combat_type, damage_type, can_dual, can_shield, can_parry, handed_override
            "Shield":       WeaponType(self.owner, 'Shield', 'melee', 'Shield', False, True, True, False),
            "Short Sword":  WeaponType(self.owner, 'Short Sword', 'melee', 'Slash', True, True, False, False),
            "Long Sword":   WeaponType(self.owner, 'Long Sword', 'melee', 'Slash', False, False, False, False),
            "Great Sword":  WeaponType(self.owner, 'Great Sword','melee', 'Slash', False, False, False, False),
            "Hand Axe":     WeaponType(self.owner, 'Hand Axe', 'melee', 'Slash', True, True, False, False),
            "Battle Axe":   WeaponType(self.owner, 'Battle Axe', 'melee', 'Slash', False, False, False, False),
            "Throwing Axe": WeaponType(self.owner, 'Throwing Axe', 'ranged', 'Slash', False, False, False, False),
            "Mace":         WeaponType(self.owner, 'Mace', 'melee', 'Smash', False, True, False, False),
            "Hammer":       WeaponType(self.owner, 'Hammer', 'melee', 'Smash', False, True, False, False),
            "Great Hammer": WeaponType(self.owner, 'Great Hammer', 'melee', 'Smash', False, False, False, False),
            "Flail":        WeaponType(self.owner, 'Flail', 'melee', 'Smash', False, False, False, False),
            "Staff":        WeaponType(self.owner, 'Staff', 'melee', 'Smash', False, False, False, False),
            "Sling":        WeaponType(self.owner, 'Sling', 'ranged', 'Smash', False, True, False, False),
            "Bow":          WeaponType(self.owner, 'Bow', 'ranged', 'Stab', False, False, False, False),
            "Crossbow":     WeaponType(self.owner, 'Crossbow', 'ranged', 'Stab', True, True, False, False),
            "Dagger":       WeaponType(self.owner, 'Dagger', 'melee', 'Stab', True, True, False, False),
            "Throw Dagger": WeaponType(self.owner, 'Throw Dagger', 'ranged', 'Stab', False, False, False, False),
            "Polearm":      WeaponType(self.owner, 'Polearm', 'melee', 'Stab', False, False, False, False),
            "Javelin":      WeaponType(self.owner, 'Javelin', 'ranged', 'Stab', False, False, False, False),
        }

        # self.weapon_panel_key = ['Combat Type', 'Damage Type', 'Can Dual', 'Can Shield', 'Level', 'EXP', 'Can Parry',
        #                          '2h override']
        # self.weapon_panel = {  # do not change indexes of values, add new values to end of arrays, TY!
        #     #   Key:        [combat_type, damage_type, can_dual, can_shield, level, xp, can_parry, handed_override}
        #     "Shield": ['melee', 'Shield', False, True, 1, 0, True, False],  #
        #     "Short Sword": ['melee', 'Slash', True, True, 1, 0, False, False],  #
        #     "Long Sword": ['melee', 'Slash', False, False, 1, 0, False, False],  #
        #     "Great Sword": ['melee', 'Slash', False, False, 1, 0, False, False],  #
        #     "Hand Axe": ['melee', 'Slash', True, True, 1, 0, False, False],  #
        #     "Battle Axe": ['melee', 'Slash', False, False, 1, 0, False, False],  #
        #     "Throwing Axe": ['ranged', 'Slash', False, False, 1, 0, False, False],  #
        #     "Mace": ['melee', 'Smash', False, True, 1, 0, False, False],  #
        #     "Hammer": ['melee', 'Smash', False, True, 1, 0, False, False],  #
        #     "Great Hammer": ['melee', 'Smash', False, False, 1, 0, False, False],  #
        #     "Flail": ['melee', 'Smash', False, False, 1, 0, False, False],  #
        #     "Staff": ['melee', 'Smash', False, False, 1, 0, False, False],  #
        #     "Sling": ['ranged', 'Smash', False, True, 1, 0, False, False],  #
        #     "Bow": ['ranged', 'Stab', False, False, 1, 0, False, False],  #
        #     "Crossbow": ['ranged', 'Stab', True, True, 1, 0, False, False],  #
        #     "Dagger": ['melee', 'Stab', True, True, 1, 0, False, False],  #
        #     "Throw Dagger": ['ranged', 'Stab', False, False, 1, 0, False, False],  #
        #     "Polearm": ['melee', 'Stab', False, False, 1, 0, False, False],  #
        #     "Javelin": ['ranged', 'Stab', False, False, 1, 0, False, False],  #
        # }

        self.equipped = {  # Key: 'location' : item
            '1h': None,
            '2h': None,
            'Head': None,
            'Shoulders': None,
            'Arms': None,
            'Hands': None,
            'Torso': None,
            'Legs': None,
            'Feet': None,
            'Cloak': None,
            'Neck': None,
            'Ring': None
        }
        self.impaled = {
            'Torso': [],
            'Head':  [],
            'Arms':  [],
            'Legs':  []
        }
        self.armor_panel = {
            #   Key:
            "Head": [],
            "Shoulders": [],
            "Arms": [],
            "Hands": [],
            "Torso": [],
            "Legs": [],
            "Feet": [],
            "Cloak": [],
            "Neck": [],
            "Ring": [],
        }
        self.ammo_types_key = []  # TODO add things like skill based range modifiers or flags for ammo type bonuses
        self.ammo_types = {
            # "Throwing Axe": [],
            "Sling": [],
            "Bow": [],
            "Crossbow": [],
            # "Throw Dagger": [],
            # "Javelin": []
        }
        # Armor types thought process:
        # Fully naked is the only way to level None, but should provide sick end game benefits if you survive
        # Wearing at least 1 piece of armor levels that type - if it is the only type equipped
        # Wearing multiple types, you will level the type with slot majority
        # If slot diversity is equal across types you will level the heaviest type worn
        # ***OR***
        # We could do a 1 point per gear slot exp distribution to level multiple types slower but simultaneously
        #       vs wearing all one type and becoming more proficient in a single type
        self.armor_types_key = ["Level", "Exp"]
        self.armor_types = {
            "Heavy": [1, 0],
            "Light": [1, 0],
            "Robe": [1, 0],
            "None": [1, 0]
        }
        # using a weapon of a particular size will make you better with that size
        self.gear_sizes = ["tiny", "small", "normal", "large", "huge"]

    ############################################################
    # EQUIP / UNEQUIP + ACTIVATE / DEACTIVATE ##################
    ############################################################
    def quip_it(self, gear):
        """
            it rubs the gears on its skin
        :param gear: the gear to quip
        """
        if self.is_light(gear):
            if self.light_source is not None:
                self.unquip_it(self.light_source)
            self.light_source = gear

        elif self.is_weapon(gear):
            if self.is_two_hander(gear):  # emtpy both hands and equip
                if self.equipped['1h'] is not None:
                    self.unquip_it(self.equipped['1h'])
                if self.equipped['2h'] is not None:
                    self.unquip_it(self.equipped['2h'])
                self.equipped['1h'] = gear
                self.equipped['2h'] = None
            else:  # deal with single handed weapons
                hand_to_equip = '1h'
                if self.equipped['1h'] is not None:
                    if self.can_dual(self.equipped['1h']) and self.can_dual(gear):
                        if self.equipped['2h'] is not None:
                            self.unquip_it(self.equipped['2h'])
                        hand_to_equip = '2h'
                    elif self.is_shield(gear):  # must remove shield to dual
                        if self.equipped['2h'] is not None:
                            self.unquip_it(self.equipped['2h'])
                        hand_to_equip = '2h'
                    else:
                        self.unquip_it(self.equipped['1h'])
                self.equipped[hand_to_equip] = gear

        elif self.is_shield(gear):
            if self.is_two_hander(self.equipped['1h']):
                self.unquip_it(self.equipped['1h'])
            if self.equipped['2h'] is not None:
                self.unquip_it(self.equipped['2h'])
            self.equipped['2h'] = gear
            self.activate_shield(gear)

        elif self.is_armor(gear):
            if self.equipped[gear.item.equipment.location] is not None:
                self.unquip_it(self.equipped[gear.item.equipment.location])
            self.equipped[gear.item.equipment.location] = gear
            self.activate_armor(gear)

        elif gear.item.equipment.type == 'monster_melee':  # this is just to hopefully catch any with no subtype
            self.equipped['1h'] = gear

        if len(gear.item.equipment.effects) > 0:
            self.activate_effects(gear)
        # self.activate_mods(gear)
        # self.activate_perks(gear) # TODO WE GOT PERKS BITCH
        if self.owner.game.player.fighter == self.owner:
            if gear in self.owner.inventory:
                # TODO CONSIDER:should only do this if equip is successful? is that an issue?
                self.owner.inventory.remove(gear)
            self.owner.game.message.message(gear.name + " equipped.", 1)  # this is getting sent to flavor_country

    def unquip_it(self, gear):
        """
            nothing lasts forever
        :param gear: the gear to unquip
        """
        # if gear not in self.equipped.values(): # don't do anything if the gear to unequip is not equipped
        #    return

        if len(gear.item.equipment.effects) > 0:
            self.deactivate_effects(gear)

        if self.is_light(gear):
            self.light_source = None
        if self.is_weapon(gear):
            if self.equipped['1h'] == gear:
                self.equipped['1h'] = None
            elif self.equipped['2h'] == gear:
                self.equipped['2h'] = None
        elif self.is_shield(gear):
            self.equipped['2h'] = None
        elif self.is_armor(gear):
            self.equipped[gear.item.equipment.location] = None
            self.activate_armor(gear)

        # self.deactivate_mods(gear)
        # self.deactivate_perks(gear)  # TODO WE GOT PERKS BITCH
        self.owner.inventory.append(gear)
        self.owner.game.message.message(gear.name + " unequipped.", 1)  # this is getting sent to flavor_country

    def activate_effects(self, gear):
        """ activates all the effects on a passed gear to the owner's stat panel """
        for effect in gear.item.equipment.effects:
            effect.activate_effect(self.owner)

    def deactivate_effects(self, gear):
        """ deactivates all the effects on a passed gear from the owner's stat panel """
        for effect in gear.item.equipment.effects:
            effect.deactivate_effect()

    def activate_armor(self, gear):
        """ adds an armor's defense and evasion amounts to stat panel """
        armor_bonus = gear.item.equipment.bonus if gear in self.equipped.values() else gear.item.equipment.bonus * -1
        armor_pen = gear.item.equipment.penalty if gear in self.equipped.values() else gear.item.equipment.penalty * -1

        new_def = self.owner.stat.get_stat_mod("Defense") + armor_bonus
        self.owner.stat.set_stat_mod("Defense", new_def)
        new_pen = self.owner.stat.get_stat_pen("Evasion") + armor_pen
        self.owner.stat.set_stat_pen("Evasion", new_pen)

    def activate_shield(self, gear):
        """ adds a shield's block amount to stat panel """
        block_chance = gear.item.equipment.accuracy if gear in self.equipped.values() else gear.accuracy * -1

        new_block = self.owner.stat.get_stat_mod("Block") + block_chance
        self.owner.stat.set_stat_mod("Block", new_block)
        # TODO Figure in size comparison and accuracy +/- as well as min-max damage mitigation

    ####################################
    # UTILITY ##########################
    ####################################
    def gimmie_da_quips(self):
        """ :return: array of equipment objects, sort it yourself! """
        return list(self.equipped.values())

    def gimmie_da_weapon(self, off_hand=False):
        """ :return:  da weapon, pick a hand! """
        if off_hand and self.equipped['2h'] is not None:
            return self.equipped['2h']
        elif self.equipped['1h'] is not None:
            return self.equipped['1h']

    def gimmie_da_armors(self):
        """ :return:  you guessed it """
        da_armors = []
        for slot_location in self.armor_panel.keys():
            da_armors.append(self.equipped[slot_location])
        return da_armors  # to me now!

    def gimmie_da_slots(self):
        """ :return: list of armor slots only (not actual gear) """
        return list(self.armor_panel.keys())

    def gimmie_da_slots_all(self):
        """ :return: list of equipment slots, weapons and armor (not the actual gear) """
        return list(self.equipped.keys())

    def get_quipped_weapon_type(self, off_hand=False):
        """ :return:  the type of weapon the fighter has """
        if off_hand and self.equipped['2h'] is not None:
            return self.equipped['2h'].item.equipment.subtype
        elif self.equipped['1h'] is not None:
            return self.equipped['1h'].item.equipment.subtype

    def get_weapon_damage_type(self, gear):
        return self.weapon_panel[gear.item.equipment.subtype].damage_type

    def is_weapon(self, gear):
        """ returns true if the passed gear has an associated weapon type
            *NOTE* monster melee will returns false """
        if gear:
            if hasattr(gear.item.equipment, 'subtype'):
                if gear.item.equipment.subtype in self.weapon_panel.keys() and gear.item.equipment.subtype != "Shield":
                    return True
            else:
                print("Definitely not a weapon")

    def is_shield(self, gear):
        """ returns true if the passed gear is a shield... fuck """
        if gear:
            if hasattr(gear.item.equipment, 'subtype'):
                if gear.item.equipment.subtype == "Shield":
                    return True
            else:
                print("Definitely not a shield")

    def is_two_hander(self, gear):
        """ return true if the base weapon is a zweihander - *does nothing with 2h override* """
        if gear:
            if gear.item.equipment.handed == 2:
                return True

    def can_dual(self, gear):
        """ returns true if the gear passed can be equipped as dual weapons """
        if gear:
            if hasattr(gear.item.equipment, 'subtype'):
                return self.weapon_panel[gear.item.equipment.subtype].can_dual

    def can_parry(self, gear):
        """ returns true if the passed gear can parry """
        if gear:
            if hasattr(gear.item.equipment, 'subtype') and gear.item.equipment.type != 'monster_melee':
                return self.weapon_panel[gear.item.equipment.subtype].can_parry

    def is_armor(self, gear):
        """ returns true if the passed gear is an armor type """
        if gear:
            if gear.item.equipment.location in self.armor_panel.keys():
                return True

    def is_light(self, gear):
        """ returns true if the passed gear is a light """
        if gear:
            if gear.item.equipment.type == 'light_source':
                return True

    def get_2h_override(self, gear):
        """ returns weapon's equip type override """
        if gear:
            if self.is_weapon(gear) or self.is_shield(gear):
                return self.weapon_panel[gear.item.equipment.subtype].handed_override

    def get_w_xptnl(self, wep_type):
        """ calculates exp tnl based on current level """
        # TODO BALANCING change weapon xp tnl calc, if changed here also change in w_lvl_up
        return (self.get_w_lvl(wep_type) * 500)

    def get_w_xp(self, wep_type):
        """ gets current xp of weapon type """
        return self.weapon_panel[wep_type].xp

    def get_w_lvl(self, wep_type):
        """ pass weapon type, get it's level """
        if wep_type in self.weapon_panel:
            return self.weapon_panel[wep_type].level
        else:
            return 1

    def w_lvl_up(self, wep_type):
        """ add 1 to level, reduce current exp back to 0"""
        self.weapon_panel[wep_type].xp -= self.get_w_xptnl(wep_type)  # reset exp
        self.weapon_panel[wep_type].level += 1  # add to level

    def add_w_xp(self, amount):
        """ pass the amount of exp earned, also adds damage type exp at a set amount
            1h+shield = full xp to both
            dual wield = half xp to each
            single weapon = full exp  """
        # This is probably gonna need to do something about monster melee
        main_hand = self.gimmie_da_weapon()
        main_type = self.get_quipped_weapon_type()
        off_hand = self.gimmie_da_weapon(off_hand=True)
        off_type = self.get_quipped_weapon_type(off_hand=True)

        if main_hand and off_hand:
            if self.is_shield(off_hand): # 1h+shield = full exp
                self.weapon_panel[main_type].xp += amount
                self.add_damage_type_xp(self.get_weapon_damage_type(main_hand))
                self.weapon_panel[off_type].xp += amount
                self.add_damage_type_xp(self.get_weapon_damage_type(off_hand))
            else: # duals split exp to each hand
                self.weapon_panel[main_type].xp += int(amount / 2)
                self.weapon_panel[off_type].xp += int(amount / 2)
                self.add_damage_type_xp(self.get_weapon_damage_type(main_hand))
                self.add_damage_type_xp(self.get_weapon_damage_type(off_hand))
        if main_hand and not off_hand:
            self.weapon_panel[main_type].xp += amount
            self.add_damage_type_xp(self.get_weapon_damage_type(main_hand))
        if off_hand and not main_hand:
            self.weapon_panel[off_type].xp += amount
            self.add_damage_type_xp(self.get_weapon_damage_type(off_hand))

        if self.weapon_panel[main_type].xp > self.get_w_xptnl(main_type):
            self.w_lvl_up(main_type)
        if self.weapon_panel[off_type].xp > self.get_w_xptnl(off_type):
            self.w_lvl_up(off_type)

    def add_damage_type_xp(self, damage_type):
        """" adds 1 xp per kill, levels it up every 1000 """
        self.damage_types[damage_type].xp += 1
        self.damage_types[damage_type].check_for_level_up()

    #########################################
    # COMBAT ################################
    #########################################
    def get_weapon_damage(self):  # TODO consider idk if i like this here
        """ gets the damage range for one or both weapons and returns a random final value """
        main_hand = self.gimmie_da_weapon()
        off_hand = self.gimmie_da_weapon(off_hand=True)
        min_dmg = 0
        max_dmg = 0

        if not main_hand and not off_hand:
            max_dmg = 1

        if main_hand:
            min_dmg = main_hand.item.equipment.damage[0]
            max_dmg = main_hand.item.equipment.damage[1]
        if off_hand and not self.is_shield(off_hand):
            min_dmg += off_hand.item.equipment.damage[0]
            max_dmg += off_hand.item.equipment.damage[1]

            # TODO further factor in weapon bonuses ( perks / skills / w.lvls ) ??
        final_damage = libtcod.random_get_int(0, min_dmg, max_dmg)
        # TODO apply weapon level bonus damage to stat panel, not direct:
        # if main_hand.type != 'monster_melee':
        #    final_damage += + int(self.get_w_lvl(main_hand.subtype) / 4)

        return final_damage

    def get_gear_size_modifier(self, size_a, size_b):
        """ pass 2 sizes, returns a multiplier in the range of -4 to 4 """
        # TODO gear doesnt have sizes importing yet, do that or bork
        gear_a_rating = self.gear_sizes.index(size_a)
        gear_b_rating = self.gear_sizes.index(size_b)
        modifier = gear_a_rating - gear_b_rating
        return modifier

    def get_combat_type(self):
        """ returns the combat type of your main hand weapon - ranged or melee
            if no main hand weapon, checks off hand for weapon,
            if none returns None """
        weapon = self.gimmie_da_weapon()
        off_hand_weapon = self.gimmie_da_weapon(off_hand=True)
        if weapon:
            return self.weapon_panel[weapon.item.equipment.subtype].combat_type
        else:
            if off_hand_weapon:  # and self.is_weapon(off_hand_weapon):
                return self.weapon_panel[weapon.item.equipment.subtype].combat_type
        return None

    #######################################
    # INTERFACE ###########################
    #######################################
    def compare_gear(self, gear_to_compare):  # TODO Finish later, use hover_descriptions
        if gear_to_compare not in self.equipped.values():
            names = ["Current:"]
            if self.is_weapon(gear_to_compare):
                names.append(self.equipped[gear_to_compare.subtype].owner.name)
                # names.append(self.equipped)
            if self.is_armor(gear_to_compare):
                names.append(self.equipped[gear_to_compare.location])

    def get_ammo_types(self):
        return list(self.ammo_types.keys())