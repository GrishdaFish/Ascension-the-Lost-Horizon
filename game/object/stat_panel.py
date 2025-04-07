__author__ = 'noobspanker'

import tcod as libtcod


class StatPanel:
    """
        StatPanel is attached to all instances of fighter to track and adjust effects and conditions.
    """
    def __init__(self):
        # panel will maintain a working reference to all modifiable/persistent stats and has getters and setters
        # never make changes to the panel directly and it will always work the right way
        self.panel = {
            "modifiers": {
                "key": ["Penalty", "Modifier", "Base"],
                "HP": [0, 0, 999999],
                "Regen": [0, 0, 0],
                "Accuracy": [0, 0, 1],
                "Defense": [0, 0, 1],
                "Block": [0, 0, 0],
                "Parry": [0, 0, 0],
                "Evasion": [0, 0, 0],
                "Speed": [0, 0, 10],
                "Strength": [0, 0, 10],
                "Constitution": [0, 0, 10],
                "Dexterity": [0, 0, 10],
                "Intelligence": [0, 0, 10],
            },
            "elemental": {
                "key": ["Damage", "Resistance", "Color"],
                "Fire": [0, 0, libtcod.red],
                "Ice": [0, 0, libtcod.light_blue],
                "Stone": [0, 0, libtcod.grey],
                "Storm": [0, 0, libtcod.light_purple],
                "Holy": [0, 0, libtcod.gold],
                "Evil": [0, 0, libtcod.dark_grey],
                # physical damage/resistance
                #      "Poison": [0, 0, libtcod.green],
                #      "Bleed": [0, 0, libtcod.dark_crimson],
                # physical state rate/resistance
                # "Crit Rate": [0, 0, libtcod.light_grey],   # to crit and to evade crit rates stored here
                # "Crit Damage": [0, 0, libtcod.light_grey]  # crit damage and crit damage resist stored here
                # petrify ?
            },
            "conditions": {
                # conditions the actor can cause / resist
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
        }

        self.active_conditions = []     # tracks afflicted conditions
        self.elemental_effects = []     # tracks actor's equipped elemental effects
        self.modifiers = []             # tracks actor's equipped modifiers
        self.conditions = []            # tracks actor's equipped inflict-able conditions

    def apply_effect(self, effect):
        """ Called by an effect object to register itself to the panel
        :param effect: the effect instance being registered
        """
        if effect.panel_group == 'modifiers':
            if effect.index == 0:  # 0 is penalty index,
                self.set_stat_pen(effect.effect_name, (self.get_stat_pen(effect.effect_name) + effect.amount))  # add to mod amount
            if effect.index == 1:  # 1 is modifier index
                self.set_stat_mod(effect.effect_name, (self.get_stat_mod(effect.effect_name) + effect.amount))   # add to mod amount
            self.modifiers.append(effect)
        if effect.panel_group == 'elemental':
            if effect.index == 0:
                self.set_elemental_damage(effect.effect_name, (self.get_elemental_damage(effect.effect_name) + effect.amount))
            if effect.index == 1:
                self.set_elemental_resist(effect.effect_name, (self.get_elemental_resist(effect.effect_name) + effect.amount))
            self.elemental_effects.append(effect)
        if effect.panel_group == 'conditions':
            if effect.index == 0:
                self.set_condition_damage(effect.effect_name, (self.get_condition_damage(effect.effect_name) + effect.amount))
                self.set_condition_rate(effect.effect_name, (self.get_condition_rate(effect.effect_name) + effect.probability))
            if effect.index == 1:
                self.set_condition_resist(effect.effect_name, (self.get_condition_resist(effect.effect_name) + effect.amount))
            self.conditions.append(effect)

    def remove_effect(self, effect):
        """ Called by an effect object to deactivate from the panel
        :param effect: the effect instance to deactivate
        """
        if effect.panel_group == 'modifiers':
            if effect.index == 0:  # 0 is penalty index,
                self.set_stat_base(effect.effect_name, (self.get_stat_base(effect.effect_name) + effect.amount))  # add to total
                self.set_stat_pen(effect.effect_name, (self.get_stat_pen(effect.effect_name) - effect.amount))  # add to pen amount
            if effect.index == 1:  # 1 is modifier index
                self.set_stat_base(effect.effect_name, (self.get_stat_base(effect.effect_name) - effect.amount))  # add to total
                self.set_stat_mod(effect.effect_name, (self.get_stat_mod(effect.effect_name) - effect.amount))   # add to mod amount
            self.modifiers.remove(effect)
        if effect.panel_group == 'elemental':
            if effect.index == 0:
                self.set_elemental_damage(effect.effect_name, (self.get_elemental_damage(effect.effect_name) - effect.amount))
            if effect.index == 1:
                self.set_elemental_resist(effect.effect_name, (self.get_elemental_resist(effect.effect_name) - effect.amount))
            self.elemental_effects.remove(effect)
        if effect.panel_group == 'conditions':
            if effect.index == 0:
                self.set_condition_damage(effect.effect_name, (self.get_condition_damage(effect.effect_name) - effect.amount))
                self.set_condition_rate(effect.effect_name, (self.get_condition_rate(effect.effect_name) - effect.amount))
            if effect.index == 1:
                self.set_condition_resist(effect.effect_name, (self.get_condition_resist(effect.effect_name) - effect.amount))
            self.conditions.remove(effect)

    def effect_is_active(self, effect):
        """ Determines if an effect is currently activated for use on this stat_panel
        :param effect: the effect instance to compare
        :return: True if active, duh
        """
        if effect.panel_group == 'modifiers':
            if effect in self.modifiers:
                return True
        if effect.panel_group == 'elemental':
            if effect in self.elemental_effects:
                return True
        if effect.panel_group == 'conditions':
            if effect in self.conditions:
                return True
        return False

    def apply_condition(self, effect):
        """ checks for stacking and afflicts condition """
        stacked_conditions = []
        for fx in self.active_conditions:
            if fx.effect_name == effect.effect_name:
                stacked_conditions.append(fx)
        if len(stacked_conditions) >= effect.max_stack:
            self.remove_condition(self.find_lowest_duration(stacked_conditions))
        self.active_conditions.append(effect)
        effect.add_turn()

    def find_lowest_duration(self, stack):
        """ checks which of your afflicted conditions has the lowest duration remaining """
        lowest_duration = None
        for fx in stack:
            if lowest_duration is None or fx.duration < lowest_duration.duration:
                lowest_duration = fx
        return lowest_duration

    def remove_condition(self, effect):
        """ removes an afflicted condition """
        if effect in self.active_conditions:
            self.active_conditions.remove(effect)

    ###################################################################################################################
    # self.panel.modifiers access #####################################################################################
    ###################################################################################################################
    def get_stat(self, name):
        """     Calculates the total value of the stat ( Base + Mods - Pens = this )
        :param name:  the stat you want
        :return: also, the stat you want
        """
        total_stat = self.get_stat_base(name)
        total_stat += self.get_stat_mod(name)
        total_stat -= self.get_stat_pen(name)
        return total_stat

    def set_stat_base(self, name, amount):
        """ the base is for permanent changes: potion of permanent reduce strength, level up, etc.
        :param name: name of the base stat in self.panel['modifiers'] to change
        :param amount: amount to set it to
        """
        if name in self.panel['modifiers'].keys():
            self.panel['modifiers'][name][2] = amount

    def get_stat_base(self, name):
        """ returns the base amount for the named stat
        :param name: name of the base stat in self.panel['modifiers'] to get
        :return: current value of 'name' stat
        """
        if name in self.panel['modifiers'].keys():
            return self.panel['modifiers'][name][2]

    def set_stat_mod(self, name, amount):
        """ the modifier is for all beneficial non-permanent changes from items, potions, spells etc. """
        if name in self.panel['modifiers'].keys():
            self.panel['modifiers'][name][1] = amount

    def get_stat_mod(self, name):
        """ returns the current modifier amount for the named stat """
        if name in self.panel['modifiers'].keys():
            return self.panel['modifiers'][name][1]

    def set_stat_pen(self, name, amount):
        """ the oenalty holds all negative non-permanent changes to a stat from items, potions, spells etc. """
        if name in self.panel['modifiers'].keys():
            self.panel['modifiers'][name][0] = amount

    def get_stat_pen(self, name):
        """ returns the current penalty for the named stat """
        if name in self.panel['modifiers'].keys():
            return self.panel['modifiers'][name][0]

    def get_all_base_stats(self):
        """ called to get data before packing and passing to server """
        stat_array = []
        for stat in list(self.panel['modifiers'].keys()):
            if stat != "key":
                stat_array.append(self.get_stat_base(stat))
        return stat_array

    def set_all_base_stats(self, stat_array):
        """ called to set data sent from server """
        i = 0
        for stat in list(self.panel['modifiers'].keys()):
            if stat != "key":
                self.set_stat_base(stat, int(stat_array[i]))
                i += 1

    ###################################################################################################################
    # self.panel.elemental access #####################################################################################
    # *the following functions take only the name, not the effect object. #############################################
    ###################################################################################################################
    def get_total_elemental_damage(self):
        """ gets damage total for all elements """
        # TODO this isn't finished O.o
        total_damage = 0
        for key, val in self.panel['elemental']:
            if key != "key" and isinstance(val[0], int):
                total_damage += val[0]

    def set_elemental_damage(self, name, amount):
        """ sets new damage amount, overwrites - does not add """
        if name in self.panel['elemental'].keys():
            self.panel['elemental'][name][0] = amount

    def get_elemental_damage(self, name):
        """ gets damage total for single element """
        if name in self.panel['elemental'].keys():
            return self.panel['elemental'][name][0]

    def set_elemental_resist(self, name, amount):
        """ sets new resistance amount, overwrites - does not add """
        if name in self.panel['elemental'].keys():
            self.panel['elemental'][name][1] = amount

    def get_elemental_resist(self, name):
        """ gets resist amount for a single element """
        if name in self.panel['elemental'].keys():
            return self.panel['elemental'][name][1]

    # Damage=True to return array of elemental damages, False for resistances
    def get_elem_array(self, resist=False):
        """ :return an array of all elemental damages or all resists """
        val_index = 0
        if resist:
            val_index = 1
        val_array = []
        for element in self.panel['elemental'].keys():
            if element != "key":
                val_array.append(self.panel['elemental'][element][val_index])
        return val_array

    ###################################################################################################################
    # self.panel.conditions access ####################################################################################
    # *the following functions take only the name, not the effect object. #############################################
    ###################################################################################################################
    def set_condition_damage(self, name, amount):
        """ sets new damage amount, overwrites - does not add """
        if name in self.panel['conditions'].keys():
            self.panel['conditions'][name][0] = amount

    def get_condition_damage(self, name):
        """ gets damage total """
        if name in self.panel['conditions'].keys():
            return self.panel['conditions'][name][0]

    def set_condition_resist(self, name, amount):
        """ sets new resistance amount, overwrites - does not add """
        if name in self.panel['conditions'].keys():
            self.panel['conditions'][name][1] = amount

    def get_condition_resist(self, name):
        """ get resistance amount """
        if name in self.panel['conditions'].keys():
            return self.panel['conditions'][name][1]

    def set_condition_rate(self, name, amount):
        """ sets new probability of landing, overwrites - does not add """
        if name in self.panel['conditions'].keys():
            self.panel['conditions'][name][2] = amount

    def get_condition_rate(self, name):
        """ get probability of landing """
        if name in self.panel['conditions'].keys():
            return self.panel['conditions'][name][2]

    ###################################################################################################################
    # utility functions ###############################################################################################
    ###################################################################################################################

    def get_effect_color(self, effect):
        """
        :param effect: an effect object instance
        :return: libtcod.color associated with the effect
        """
        if effect.panel_group == 'modifier':  # this is redundant, as none is returned either way, however:
            return None  # inject here if color is added to base stats. seems better to keep them white to me
        if effect.panel_group == 'elemental':
            return self.panel['elemental'][effect.effect_name][2]
        if effect.panel_group == 'conditions':
            return self.panel['conditions'][effect.effect_name][3]

    def get_category_count(self, category):
        """ stupid display assist function called by character.py """
        return len(self.panel[category])

    def destroy(self):
        """ set object containers to none, call when monsters die """
        self.active_conditions = None
        self.elemental_effects = None
        self.modifiers = None
        self.conditions = None

    def get_total_threat(self):
        threat = 0
        threat += self.get_stat("HP")
        threat += self.get_stat("Regen") * 2
        threat += self.get_stat("Accuracy")
        threat += self.get_stat("Defense")
        threat += self.get_stat("Block")
        threat += self.get_stat("Parry")
        threat += self.get_stat("Evasion")
        threat += self.get_stat("Speed") / 10
        threat += self.get_stat("Strength") / 10
        threat += self.get_stat("Constitution") / 10
        threat += self.get_stat("Dexterity") / 10
        threat += self.get_stat("Intelligence") / 10