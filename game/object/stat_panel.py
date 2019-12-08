__author__ = 'noobspanker'
import tcod as libtcod
from game.object.conditions import ConditionManager


class StatPanel:
    """
        StatPanel is attached to all instances of fighter to track and adjust effects and conditions.
    """
    def __init__(self):
        # panel will maintain a working reference to all modifiable/persistent stats and has getters and setters
        # never make changes to the panel directly and it will always work the right way
        #             "Light-based effects" : Not sure yet #TODO  <- consider how id like to do this
        self.panel = {
            "modifiers": {
                # [base stat value, modifier, penalty]
                "HP": [15, 0, 0],
                "Regen": [0, 0, 0],
                "Defense": [1, 0, 0],
                "Evasion": [1, 0, 0],
                "Strength": [10, 0, ],
                "Constitution": [10, 0, 0],
                "Dexterity": [10, 0, 0],
                "Intelligence": [10, 0, 0],
                "Speed": [10, 0, 0],
            },
            "combat": {
                # [elemental damage, resist, display color]
                "key": ["Damage", "Resistance", "Color"],
                "Fire": [0, 0, libtcod.red],
                "Ice": [0, 0, libtcod.light_blue],
                "Stone": [0, 0, libtcod.grey],
                "Storm": [0, 0, libtcod.light_purple],
                "Holy": [0, 0, libtcod.gold],
                "Evil": [0, 0, libtcod.dark_grey],
                # physical damage/resistance
                "Poison": [0, 0, libtcod.green],
                "Bleed": [0, 0, libtcod.dark_crimson],
                # physical state rate/resistance
                "Crit Rate": [0, 0, libtcod.light_grey],   # to crit and to evade crit rates stored here
                "Crit Damage": [0, 0, libtcod.light_grey]  # crit damage and crit damage resist stored here
                # petrify ?
            },
            "conditions": {
                # conditions the actor can cause / resist [damage, resistance, inflict_rate, display color]
                "key": ["Damage", "Resistance", "Rate", "Color"],
                "Burn":  [0, 0, 0, libtcod.red],
                "Freeze":  [0, 0, 0, libtcod.light_blue],
                "Tremor":  [0, 0, 0, libtcod.grey],
                "Shock":  [0, 0, 0, libtcod.light_purple],
                "Smite":  [0, 0, 0, libtcod.gold],
                "Corrupt":  [0, 0, 0, libtcod.dark_grey],
                "Plague":  [0, 0, 0, libtcod.green],
                "Gash":  [0, 0, 0, libtcod.dark_crimson],
                "Stun": [0, 0, 0, libtcod.orange],
                "Blind": [0, 0, 0, libtcod.lightest_gray],
            }
            # dodge, armor, weapon, etc can all be stored here as well
        }

        self.condition_manager = ConditionManager()    # tracks afflicted conditions
        self.combat_effects = []                # tracks actor's equipped combat effects
        self.modifiers = []                     # tracks actor's equipped modifiers
        self.conditions = []                    # tracks actor's equipped inflict-able conditions

    def apply_effect(self, effect):
        """
            Called by an effect to register itself
        :param effect: the effect instance being registered
        """
        if effect.panel_group == 'modifiers':
            self.set_stat_by_name(effect, True, True)  # add to total
            self.modifiers.append(effect)
        if effect.panel_group == 'combat':
            self.set_combat_stat_by_name(effect, True)
            self.combat_effects.append(effect)
        if effect.panel_group == 'conditions':
            self.set_condition_stat_by_name(effect, True)
            self.conditions.append(effect)

    def remove_effect(self, effect):
        """
            Called by an effect to be de activated
        :param effect: the effect instance to de activate
        """
        if effect.panel_group == 'modifiers' and effect in self.modifiers:
            self.modifiers.remove(effect)
            self.set_stat_by_name(effect, True, True)
        if effect.panel_group == 'combat' and effect in self.combat_effects:
            self.combat_effects.remove(effect)
            self.panel[effect.panel_group][effect.effect_name][effect.index] -= effect.amount
        if effect.panel_group == 'conditions' and effect in self.conditions:
            self.conditions.remove(effect)
            self.panel[effect.panel_group][effect.effect_name][effect.index] -= effect.amount

    # call as is for bulk damage, pass True for full details
    def return_damage(self, details=False): #TODO determine desired output format / dont use details yet
        damage = 0                          #TODO i dont this this is hooked up at all?
        damage_detail = []
        if details:
            for mod, val in self.panel:
                if "Damage" in mod:
                    damage_detail.append( [mod, val] )
        else:
            group = list(self.panel['combat'])
            group.pop(0)  # pop out the key
            for value in group:
                # print(self.panel['combat'][value][0])
                damage += self.panel['combat'][value][0]
        return damage

    # stupid display assist function called by character.py
    def get_category_count(self, category):
        return len(self.panel[category])

    # determines if an effect is currently activated for use on this stat_panel
    def effect_is_active(self, effect):
        if effect.panel_group == 'modifiers':
            if effect in self.modifiers:
                return True
        elif effect.panel_group == 'combat':
            if effect in self.combat_effects:
                return True
        elif effect.panel_group == 'conditions':
            if effect in self.conditions:
                return True
        else:
            return False

    ####
    # get set radio future
    ####
    def set_stat(self, name, add=True):
        """

        :param name: name of the stat to change
        :param add: Optional parameter, set to false will overwrite instead of adding
        :return:
        """
        if name in self.panel['modifiers'].keys():
            if add:  # add to stat
                self.panel['modifiers'][name][0] = 0
            else:  # overwrite stat
                return self.panel['modifiers'][name][0]
    """    get_stat
        set_stat_mod
        get_stat_mod
        set_stat_pen
        get_stat_pen
        set_elemental_damage
        get_elemental_damage
        set_elemental_resist
        get_elemental_resist
        set_condition_damage
        get_condition_damage
        set_condition_resist
        get_condition_resist
        set_condition_rate
        get_condition_rate """
    # call (name) for stat, (name, True) for bonus amount only
    def get_stat_by_name(self, effect_name, mod_info=False):
        if mod_info:    # this returns the mod bonus only
            return self.panel['modifiers'][effect_name][1]
        else:           # this returns the total stat value
            return self.panel['modifiers'][effect_name][0]

    # call (name) for dam, (name, True) for res
    def get_combat_stat_by_name(self, effect_name, resistance=False):
        if resistance:    # this returns the elemental resistance
            return self.panel['combat'][effect_name][0]
        else:           # this returns the elemental damage
            return self.panel['combat'][effect_name][1]

    # call (name) for dam, (name, True) for res, (name, False, True) for rate
    def get_condition_stat_by_name(self, effect_name, resistance=False, probability=False):
        if resistance:    # this returns the condition resistance only
            return self.panel['conditions'][effect_name][1]
        else:
            if probability:  # this returns the rate of infliction
                return self.panel['conditions'][effect_name][2]
            else:            # this returns the condition damage
                return self.panel['conditions'][effect_name][0]

    def set_stat_by_name(self, effect, add_instead_of_set=False, change_mod=False):
        """
            :param effect -- name of the stat you want from self.panel['modifiers']
            :param add_instead_of_set -- set to true if you dont want to overwrite
            :param change_mod -- change the modifier AND the base stat
        """
        # this changes the modifier amount
        if add_instead_of_set:     # add to modifier
            self.panel['modifiers'][effect.effect_name][0] += effect.amount
            if change_mod:
                self.panel['modifiers'][effect.effect_name][1] += effect.amount
        else:
            self.panel['modifiers'][effect.effect_name][0] = effect.amount
            if change_mod:
                self.panel['modifiers'][effect.effect_name][1] = effect.amount


    def set_combat_stat_by_name(self, effect, add_instead_of_set=False):
        """
            :param effect -- name of the stat you want from self.panel['combat']
            :param add_instead_of_set -- set to true if you dont want to overwrite
        """
        if add_instead_of_set:
            self.panel['combat'][effect.effect_name][effect.index] += effect.amount
        else:         # overwrite resistance
            self.panel['combat'][effect.effect_name][effect.index] = effect.amount

    def set_condition_stat_by_name(self, effect, add_instead_of_set=False):
        """
            :param effect -- name of the stat you want from self.panel['conditions']
            :param add_instead_of_set -- set to true if you dont want to overwrite
        """
        if effect.index == 0:
            if add_instead_of_set:
                self.panel['conditions'][effect.effect_name][0] += effect.amount
                self.panel['conditions'][effect.effect_name][2] += effect.probability
            else:
                self.panel['conditions'][effect.effect_name][0] = effect.amount
                self.panel['conditions'][effect.effect_name][2] = effect.probability
        if effect.index == 1:
            if add_instead_of_set:
                self.panel['conditions'][effect.effect_name][1] += effect.amount
            else:
                self.panel['conditions'][effect.effect_name][1] = effect.amount

    #def con_bonus(self):
    #   pass
    def get_effect_color(self, effect):
        if effect.panel_group == 'modifier':  # this is redundant, as none is returned either way, however:
            return None  # inject here if color is added to base stats. seems better to keep them standard to me
        if effect.panel_group == 'combat':
            return self.panel['combat'][effect.effect_name][2]
        if effect.panel_group == 'conditions':
            return self.panel['conditions'][effect.effect_name][3]