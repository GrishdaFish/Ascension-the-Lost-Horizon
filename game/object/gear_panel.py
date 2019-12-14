__author__ = 'noobspanker'

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

[["light_source"]]
    name="lantern"
    cell="|"
    max_fuel=540
    color = [225, 225, 0]
    effect_color=[225, 225, 0]
    value=50
    intensity=0.9


self.crit_bonus = crit_bonus
self.defense = defense
self.type = type
self.location = location


self.handed = handed
self.dual_wield = dual_wield
self.damage_type = damage_type
self.threat_level = threat_level
self.allowed_materials = allowed_materials

self.bonus = bonus
self.penalty = penalty
self.description = description
self.accuracy = accuracy
self.damage = damage

self.torch = None
self.fuel = fuel
self.max_fuel = fuel
self.torch_color = color
self.torch_intensity = intensity

self.effects = []
"""

class GearPanel:
    """
        Will hold and manage all gear equipped on a figher
    """
    def __init__(self, owner):

        self.owner = owner
        self.light_source = None

        self.weapon_panel_key =  ['Combat Type', 'Damage Type', 'Can Dual', 'Can Shield', 'Level', 'EXP']
        self.weapon_panel = { # do not change indexes of values, add new values to end of arrays, TY!
            #   Key:        [combat_type, damage_type, can_dual, can_shield, level, xp}
            "Shield":       ['melee', 'Shield', False, True, 1, 0],
            "Short Sword":  ['melee', 'Slash', True, True, 1, 0],
            "Long Sword":   ['melee', 'Slash', False, False, 1, 0],
            "Great Sword":  ['melee', 'Slash', False, False, 1, 0],
            "Hand Axe":     ['melee', 'Slash', True, True, 1, 0],
            "Battle Axe":   ['melee', 'Slash', False, False, 1, 0],
            "Throwing Axe": ['ranged', 'Slash', False, False, 1, 0],
            "Mace":         ['melee', 'Smash', False, True, 1, 0],
            "Hammer":       ['melee', 'Smash', False, True, 1, 0],
            "Great Hammer": ['melee', 'Smash', False, False, 1, 0],
            "Flail":        ['melee', 'Smash', False, False, 1, 0],
            "Staff":        ['melee', 'Smash', False, False, 1, 0],
            "Sling":        ['ranged', 'Smash', False, True, 1, 0],
            "Bow":          ['ranged', 'Stab', False, False, 1, 0],
            "Crossbow":     ['ranged', 'Stab', False, True, 1, 0],
            "Dagger":       ['melee', 'Stab', True, True, 1, 0],
            "Throw Dagger": ['ranged', 'Stab', False, False, 1, 0],
            "Polearm":      ['melee', 'Stab', False, False, 1, 0],
            "Javelin":      ['ranged', 'Stab', False, False, 1, 0],
        }

        self.equipped = {  # Key: 'location' : item     # placed here so you can compare to weapons ^ / armor V
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

    def gimmie_da_quips(self):
        """
        :return: array of equipment objects, sort it yourself!
        """
        return list(self.equipped.values())

    def gimmie_da_weapon(self, off_hand=False):
        """
        :return:  da weapon, pick a hand!
        """
        if off_hand and self.equipped['2h'] is not None:
            return self.equipped['2h']
        elif self.equipped['1h'] is not None:
            return self.equipped['1h']

    def gimmie_da_armors(self):
        """
        :return:  you guessed it
        """
        da_armors = []
        for slot_location in self.armor_panel.keys():
            da_armors.append(self.equipped[slot_location])
        return da_armors  # to me now!

    def gimmie_da_slots(self):
        """
        :return: list of armor slots
        """
        return list(self.armor_panel.keys())

    def get_quipped_weapon_type(self, off_hand=False):
        """
        :return:  the type of weapon the fighter has
        """
        if off_hand and self.equipped['2h'] is not None:
            return self.equipped['2h'].item.equipment.subtype
        elif self.equipped['1h'] is not None:
            return self.equipped['1h'].item.equipment.subtype

    def quip_it(self, gear):
        """
            it rubs the gears on its skin
        :param gear: the gear to quip
        """
        #for game_obj in self.owner.inventory:
        #    print(game_obj)
        self.owner.inventory.remove(gear)   # TODO should only do this if equip is successful


        if self.is_light(gear):
            if self.light_source is not None:
                self.owner.inventory.append(self.light_source)
            self.light_source = gear

        elif self.is_weapon(gear):
            if self.is_two_hander(gear): #emtpy both hands and equip
                if self.equipped['1h'] is not None:
                    self.owner.inventory.append(self.equipped['1h'])
                if self.equipped['2h'] is not None:
                    self.owner.inventory.append(self.equipped['2h'])
                self.equipped['1h'] = gear
                self.equipped['2h'] = None
            else:  # deal with single handed weapons
                hand_to_equip = '1h'
                if self.equipped['1h'] is not None:
                    if self.can_dual(self.equipped['1h']) and self.can_dual(gear):
                        if self.equipped['2h'] is not None:
                            self.owner.inventory.append(self.equipped['2h'])
                        hand_to_equip = '2h'
                    elif self.is_shield(gear): # must remove shield to dual
                        if self.equipped['2h'] is not None:
                            self.owner.inventory.append(self.equipped['2h'])
                        hand_to_equip = '2h'
                    else:
                        self.owner.inventory.append(self.equipped['1h'])
                self.equipped[hand_to_equip] = gear

        elif self.is_shield(gear):
            if self.is_two_hander(self.equipped['1h']):
                self.owner.inventory.append(self.equipped['1h'])
            if self.equipped['2h'] is not None:
                self.owner.inventory.append(self.equipped['2h'])
            self.equipped['2h'] = gear

        elif self.is_armor(gear):       ## TODO This does not deal with rings at all
            if self.equipped[gear.item.equipment.location] is not None:
                self.owner.inventory.append(self.equipped[gear.item.equipment.location])
            self.equipped[gear.item.equipment.location] = gear

        if len(gear.item.equipment.effects) > 0:
            self.activate_effects(gear)
        # self.activate_mods(gear)
        # self.activate_perks(gear)
        #game.message.message(gear.name + " equipped.", 1) # this is getting sent to flavor_country

    def unquip_it(self, gear):
        """
            nothing lasts forever
        :param gear: the gear to unquip
        """
        #if gear not in self.equipped.values(): # don't do anything if the gear to unequip is not equipped
        #    return
        self.owner.inventory.append(gear)

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
            self.equipped[gear.item.equipment.subtype] = None
        if len(gear.item.equipment.effects) > 0:
            self.deactivate_effects(gear)
        # self.deactivate_mods(gear)
        # self.deactivate_perks(gear)

        # game.message.message(gear.name + " unequipped.", 1) # this is getting sent to flavor_country

    def activate_effects(self, gear):
        for effect in gear.item.equipment.effects:
            effect.activate_effect(self.owner)

    def deactivate_effects(self, gear):
        for effect in gear.item.equipment.effects:
            effect.deactivate_effect()

    # JUST TELL ME IF ITS A FUCKING WEAPON PLX
    def is_weapon(self, gear):
        if gear:
            if hasattr(gear.item.equipment, 'subtype'):
                if gear.item.equipment.subtype in self.weapon_panel.keys() and gear.item.equipment.subtype != "Shield":
                    return True
            else:
                print("Definitely not a weapon")

    # TELLS ME IF ITS A SHIELD
    def is_shield(self, gear):
        if gear:
            if hasattr(gear.item.equipment, 'subtype'):
                if gear.item.equipment.subtype == "Shield":
                    return True
            else:
                print("Definitely not a shield")

    # WEAPON IS A 2H
    def is_two_hander(self, gear):
        if gear:
            if gear.item.equipment.handed == 2:
                return True

    # WEAPON CAN BE DUAL EQUIPPED
    def can_dual(self, gear):
        if gear:
            return self.weapon_panel[gear.item.equipment.subtype][3]

    # TELLS ME IF ITS AN ARMOR TYPE
    def is_armor(self, gear):
        if gear:
            if gear.item.equipment.location in self.armor_panel.keys():
                return True

    # IS IT A LIGHT
    def is_light(self, gear):
        if gear:
            if gear.item.equipment.type == 'light_source':
                return True

    # GET WEAPON EXP TO NEXT LEVEL
    def get_w_xptnl(self, wep_type):
        return (self.get_w_lvl(wep_type) * 500)

    # GET WEAPON CURRENT XP AMOUNT
    def get_w_xp(self, wep_type):
        return self.weapon_panel[wep_type][5]

    # GET WEAPON TYPE LEVEL
    def get_w_lvl(self, wep_type):
        return self.weapon_panel[wep_type][4]

    # ADD XP TO WEAPON
    def add_w_xp(self, wep_type, amount):
        print(wep_type)
        self.weapon_panel[wep_type][5] += amount
        if self.weapon_panel[wep_type][5] > self.get_w_xptnl(wep_type):
            self.w_lvl_up(wep_type)

    def w_lvl_up(self, wep_type):
        self.weapon_panel[wep_type][4] += 1


    def compare_gear(self, gear_to_compare):
        pass