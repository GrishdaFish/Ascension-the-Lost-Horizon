import tcod as libtcod

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
   
     working sample as to be called from item:
         item.add_effect( self, "target", self.stat_panel.panel[index], 3, "hit", None, 65, range(4, 10), None )
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
    def __init__(self, item, actor, target, stat, max_stack, can_cancel, probability, amount, duration, speed=10):
        self.effect_name = "name"

        self.item = item            # the item that instantiated this effect, used to reference @ on_unequip in case 2 items with same effect
        self.actor = actor          # owner of this effect
        self.target = target        # STRING: "self" or "target" - who feels the effect, self - on_use, on_equip, target - on_hit
        self.stat_effected = stat   # contains stat_panel index
        self.current_stack = 0      # tracks how many times the stat has been activated
        self.max_stack = max_stack  # max times effect can stack - # TODO:this should really be predefined across the board
        # self.max_stack_concurrent = max_concurrent  # set limit for stacking same effect from multiple items? Otherwise you can stack endlessly from replenishing resources (ie buff scrolls or pots)
        self.can_cancel = can_cancel    # effect can be cancelled by item or spell (applies to status conditions)
        self.probability = probability  # % chance to trigger effect
        self.amount = amount            # strength of effect or range (+5 or +5-10) useful for damage spread or randomized outcomes
        self.duration = duration        # inflicted duration, passed to condition
        self.speed = speed              # .... speed.

    def activate_effect(self):
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
        triggered = True if libtcod.random_get_int(0, 0, 100) <= self.probability else triggered = False
        return triggered

class RandomEffectGenerator:
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
        Let's test some effects
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """

    def __init__(self):
        self.generated_effect = None

    def generate_effect(self, item, actor):
        linked_item = item
        linked_actor = actor
        target = "self" # or "target"
        # if target self stat should be beneficial ie resistance or modifier
        stat = ''
        #else stat = combat_effect
        max_stack = "" # TODO:this should really be predefined across the board
        # can cancel True if has condition
        can_cancel = ""
        # conditions have probability, otherwise it's 100
        probability = ""
        #
        amount = 0
        duration = 0
        effect = Effect(linked_item, linked_actor, target, stat, max_stack, can_cancel, probability, amount, duration)