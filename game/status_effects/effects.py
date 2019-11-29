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
    def __init__(self, item, effect):

        self.effect_name = effect   # name of the desired effect type - pull from stat_panel.panel (will make function for it)
        self.effect_type = self.get_type(effect)  # combat or modifier, so we know where to look for it in stat panel
        self.item = item            # the item that instantiated this effect, used to reference @ on_unequip in case 2 items with same effect etc.
        self.actor = None           # owner of this effect, set on activation/equip
        self.target = None          # STRING: "self" or "target" - who feels the effect, self - on_use, on_equip, target - on_hit
        self.stat_effected = None
        self.current_stack = 0      # tracks how many times the stat has been activated
        self.max_stack = 10         # max times effect can stack - 10 is arbitrary # TODO:this should really be predefined across the board
        # self.max_stack_concurrent = max_concurrent  # set limit for stacking same effect from multiple items? Otherwise you can stack endlessly from replenishing resources (ie buff scrolls or pots)
        self.can_cancel = None      # effect can be cancelled by item or spell (applies to status conditions)
        self.probability = 100      # % chance to trigger effect
        self.amount = 0             # strength of effect or range (+5 or +5-10) useful for damage spread or randomized outcomes
        self.duration = None        # inflicted duration, passed to condition
        self.speed = DEFAULT_EFFECT_SPEED   # declared above ^

        # call this to fill shit in randomly, this will be optional later on
        self.generate_effect()

    def activate_effect(self, actor):
        self.actor = actor
        if self.target == "self" and not self.duration:  # then it's a modifier
            # let's see if it's already active / at max stack
            if self in self.actor.stat_panel.modifiers or self.current_stack >= self.max_stack:
                pass  # cus that shit is already equipped / at max_stack
            else:
                self.actor.stat_panel.apply_effect(self, True)
                self.current_stack += 1
        else:  # it's not a modifier then it must be a combat effect
            if self in self.actor.stat_panel.combat_effects or self.current_stack >= self.max_stack:
                pass
            else:
                self.actor.stat_panel.apply_effect(self)
                self.current_stack -= 1

    def deactivate_effect(self):
        if self.target == "self" and not self.duration:  # then it's a modifier
            # let's make sure it's active
            if self in self.actor.stat_panel.modifiers:
                self.actor.stat_panel.remove_effect(self, True)
                self.current_stack -= 1
        else:
            if self in self.actor.stat_panel.combat_effects:
                self.actor.stat_panel.remove_effect(self)
                self.current_stack -= 1

    def trigger_probability(self):
        triggered = False
        if libtcod.random_get_int(0, 0, 100) <= self.probability:
            triggered = True
        return triggered


    def generate_effect(self):
        self.target = "target" # or "self"
        # if target self stat should be beneficial ie resistance or modifier
        #stat = ''
        #else stat = combat_effect
        #max_stack = 10 # TODO:this should really be predefined across the board
        # can cancel True if has condition
        #can_cancel = ""
        # conditions have probability, otherwise it's 100
        #probability = ""
        #
        self.amount = 5
        self.duration = 1


    def get_type(self, effect):
        stat_panel = StatPanel()
        if effect in stat_panel.panel['combat']:
            self.effect_type = 'combat'
        if effect in stat_panel.panel['modifiers']:
            self.effect_type = 'modifiers'
