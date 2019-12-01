import random

import tcod as libtcod
from game.status_effects.stat_panel import StatPanel

DEFAULT_EFFECT_SPEED = 10


class Effect:
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
        Effects categories: ones we want to test every combat round, and ones we essentially want to set and forget. 
        Rather than having a property, or creating subclass architecture we observe the properties to differentiate
        2 effect 'types': Combat effects - Alter stat temporarily or cause damage/special condition - on_use/on_hit
                          Modifiers - 'Permanently' alter a stat 1 time - on_use/on_equip - 
        modifier 'signature' can be satisfied by target and duration = (target = "self", duration = None)
     
     *** StatPanel will control tracking and containment of the 2 types as well as directly affecting stats ***
     ***    No actor stats should be edited directly in this file!                                          ***
         
     An equippable item should have an array for effects that are applied/removed @ on_equip / on_unequip
     A usable item should have an array for effects that are applied/removed @ on_use
     Weapon damage calculated must now include effect damage and test for resistances @ on_hit
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """

    def __init__(self, item, effect=None):
        # data manipulation
        self.panel_group = None  # combat modifiers or conditions, relating to stat panel.panel[panel_group]
        self.effect_name = effect  # name relating to stat_panel.panel[panel_group][name]
        self.effect_real_name = None  # name relating to stat_panel.panel[panel_group]['key'][effect_real_name] (output)
        self.index = None  # logical storage index for ease of reference
        # linked objects
        self.item = item  # the item that instantiated this effect, used to reference @ on_unequip in case 2 items with same effect etc.
        self.actor = None  # owner of this effect, set during on_equip in activate_effect

        self.amount = 0  # strength of effect *should support range (i.e +5 or +5-10) for damage spread

        # Related to conditions
        self.target = None  # actor receiving
        self.probability = 100  # % chance to trigger effect
        self.duration = None  # inflicted duration, passed to condition
        self.can_cancel = None  # effect can be cancelled by item or spell (applies to status conditions)
        self.speed = DEFAULT_EFFECT_SPEED  # declared above ^
        self.max_stack = 3  # max times effect can stack - 3 is arbitrary but will likely suffice
        # self.current_stack = 0      # tracks how many times the condition has been activated ----***Calculating this on the fly defeats the purpose of concurrent as well
        # self.max_stack_concurrent = max_concurrent  # set limit for stacking same effect from multiple items? Otherwise you can stack endlessly from replenishing resources (ie buff scrolls or pots)

        if effect is None:
            self.generate_effect()
        if self.panel_group is None:
            self.get_type()
        self.get_real_name()

    ################################################ACTIVATE/DEACTIVATE#####################################################

    # pass the actor you want to use the effect
    def activate_effect(self, actor):
        if self.actor is None:
            self.actor = actor
        self.actor.stat_panel.apply_effect(self)
#        if self.panel_group == 'modifiers':
#            if self in self.actor.stat_panel.modifiers:
#                pass  # cus that shit is already equipped / at max_stack
#            else:
#                self.actor.stat_panel.apply_effect(self)
#                # self.current_stack += 1
#        if self.panel_group == 'combat':
#            if self in self.actor.stat_panel.combat_effects:
#                pass
#            else:
#                self.actor.stat_panel.apply_effect(self)
#               # self.current_stack += 1
#        if self.panel_group == 'conditions':
#            if self in self.actor.stat_panel.conditions:
#                pass
#            else:
#                self.actor.stat_panel.apply_effect(self)
                # self.current_stack += 1

    def deactivate_effect(self, actor):
        actor.stat_panel.remove_effect(self)
        self.actor = None
#        if self.panel_group == 'modifiers':
#            # let's make sure it's active
#            if self in self.actor.stat_panel.modifiers:
#                self.actor.stat_panel.remove_effect(self)
#                # self.current_stack -= 1
#        if self.panel_group == 'combat':
#            if self in self.actor.stat_panel.combat_effects:
#                self.actor.stat_panel.remove_effect(self)
#                # self.current_stack -= 1
#        if self.panel_group == 'conditions':
#            if self in self.actor.stat_panel.conditions:
#                self.actor.stat_panel.remove_effect(self)
#                # self.current_stack -= 1

    def activate_condition(self, actor):
        # condition = hit the actor target's stat_panel.condition_manager with a new condition
        #  built from this effect's condition stats TODO <-this
        pass
    #################################################UTILITY################################################################

    def generate_effect(self):
        if self.effect_name is None:
            stat_panel = StatPanel()
            self.panel_group = random.choice(list(stat_panel.panel))
            name_list = list(stat_panel.panel[self.panel_group])

            if self.panel_group == 'modifiers':
                self.index = None
            if self.panel_group == 'combat' or self.panel_group == 'conditions':
                self.index = libtcod.random_get_int(0, 0, 1)
                name_list.pop(0)

            self.effect_name = random.choice(name_list)
        self.amount = libtcod.random_get_int(0, 1, 3)
        # self.duration = 1

    def get_type(self):
        stat_panel = StatPanel()
        if self.effect_name in stat_panel.panel['combat']:
            self.panel_group = 'combat'
        if self.effect_name in stat_panel.panel['modifiers']:
            self.panel_group = 'modifiers'
        if self.effect_name in stat_panel.panel['conditions']:
            self.panel_group = 'conditions'

    def get_real_name(self):
        stat_panel = StatPanel()
        if self.panel_group != 'modifiers':
            self.effect_real_name = stat_panel.panel[self.panel_group]['key'][self.index]
        else:
            self.effect_real_name = " "

    #####################################################COMBAT#########################################################

    def trigger_probability(self):
        triggered = False
        if libtcod.random_get_int(0, 0, 100) <= self.probability:
            triggered = True
        return triggered

    def inflict_condition(self, actor):
        if self.panel_group == 'conditions' and self.trigger_probability:
            self.activate_condition(actor)

    def inflict_damage(self):
        if self.panel_group != 'modifiers' and self.index == 0:  # damage is always the first stat in the index
            return self.amount

    def get_resistance(self, effect_name):
        if self.panel_group != 'modifiers':
            if self.effect_name == effect_name and self.index == 1:  # resistances are always second stat in the index
                return self.amount
