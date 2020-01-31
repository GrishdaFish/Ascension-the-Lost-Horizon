__author__ = 'noobspanker'
import random
import copy
import tcod as libtcod
from game.object.stat_panel import StatPanel

DEFAULT_EFFECT_SPEED = 10


class Effect:
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
           An equipment object has an array for effects that are applied/removed @ equip / unequip
        - When instantiating an effect stick it in to item.effects[] and once equipped it is activated on the actor.
        - You can also create an effect and call effect.activate(actor) to apply it directly to the actor IF PERMANENT
        - If the effect is applied directly to an actor with a temporary duration, 
                it should be passed to the ConditionManager *not implemented yet*
        
        *** StatPanel will control tracking and containment of the effects as well as directly affecting stats ***
        ***    No actor stats should be edited directly in this file!                                          ***
         
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """

    def __init__(self, item, effect=None, ticker=None):
        # linked objects
        self.actor = None  # owner of this effect, set during on_equip in activate_effect
                    # this reference persists on conditions so you can see who caused it if you care to
        self.item = item  # the item that instantiated this effect, used to reference @ on_unequip
                          # in case 2 items with same effect etc.

        # data manipulation
        self.panel_group = None    # combat modifiers or conditions, relating to stat panel.panel[panel_group]
        self.effect_name = effect  # name relating to stat_panel.panel[panel_group][name]
        self.effect_real_name = None  # name relating to stat_panel.panel[panel_group]['key'][effect_real_name] (output)
        self.index = None          # logical storage index of stat for ease of reference

        self.amount = 0            # strength of effect *should support range (i.e +5 or +5-10) for damage spread

        # Related to conditions
        self.persist = False       # is this a 1 time persistent stat modifier, like STR down or STUN?
        self.target = None         # actor receiving
        self.probability = 0       # % chance to trigger effect
        self.duration = 0         # inflicted duration in turns, passed to condition : we'll call it base 10 for now, UG w/ perks
        self.total_duration = self.duration
        self.ticker = ticker       # ***only give it a ticker if its an active condition / persist = False
        self.can_cancel = None     # effect can be cancelled by item or spell - this variable is reserved for that if needed
        self.speed = DEFAULT_EFFECT_SPEED  # declared above ^
        self.max_stack = 1         # max times effect can stack - we can start with base of 1 - not implemented

        if effect is None:
            self.generate_effect()
        if self.panel_group is None:
            self.get_type()
        self.get_real_name()

    ################################################ACTIVATE/DEACTIVATE#####################################################

    # pass the actor you want to use the effect
    def activate_effect(self, actor):
        """     activates this effect on the passed actors stat panel
        :param actor: the actor who will inflict this effect
        """
        if self.actor is None:
            self.actor = actor
        self.actor.stat.apply_effect(self)

    def deactivate_effect(self):
        """     deactivates this effect on the linked actors stat panel
        """
        if self.actor:
            self.actor.stat.remove_effect(self)
            self.actor = None

    def activate_condition(self, target):
        # checks himself in stat panel for stack-ability
        item = self.item
        actor = self.actor
        self.item = None
        self.actor = None
        condition = copy.deepcopy(self)
        condition.target = target
        condition.item = item
        condition.actor = actor
        self.item = item
        self.actor = actor
        target.stat.apply_condition(condition)

    def deactivate_condition(self):
        self.target.stat.remove_condition(self)

    def get_effect_package(self):
        """ builds its stats into a package to be rebuilt later """
        return [self.effect_name,
                self.amount,
                self.persist,
                self.probability,
                self.duration,
                self.can_cancel,
                self.speed,
                self.max_stack
                ]

    def set_from_effect_package(self, package):
        """ restores from package, see above for definition """
        self.amount = int(package[1])
        self.persist = bool(package[2])
        self.probability = int(package[3])
        self.duration = int(package[4])
        self.can_cancel = bool(package[5])
        self.speed = int(package[6])
        self.max_stack = int(package[7])

    ##################################################################
    # COMBAT #########################################################
    ##################################################################
    def trigger_probability(self, actor):
        triggered = False
        prob = self.probability - int(actor.stat.get_condition_resist(self.effect_name) / 4)  # TODO balancing
        if libtcod.random_get_int(0, 0, 100) <= prob:
            triggered = True
        return triggered

    def inflict_condition(self, actor):
        print("Trying to inflict condition")
        if self.panel_group == 'conditions' and self.trigger_probability(actor):
            print("inflicted")
            self.activate_condition(actor)

    def inflict_damage(self):
        if self.panel_group == 'conditions' and self.index == 0 and self.target is not None:  # damage is always the first stat in the index
            damage = self.amount - self.target.stat.get_condition_resist(self.effect_name)
            if self.target.hp > 0 and self.actor is not None:
                self.target.take_damage(damage, self.actor.owner, self.target.game)

    def get_resistance(self, effect_name):
        if self.panel_group != 'modifiers':
            if self.effect_name == effect_name and self.index == 1:  # resistances are always second stat in the index
                return self.amount

    ################################################################
    # CONDITIONS ###################################################
    # ##############################################################
    def use(self, game=None):
        test_out = self.effect_name + " is taking a turn. Damage:" + str(self.amount) + " To:" + self.target.owner.name
        print(test_out)
        if self.duration <= 0:            # if effect is expired kill it
            self.deactivate_condition()
        else:                               # if not, reduce duration and do stuff
            self.duration -= 1
            self.add_turn()
            if self.amount:  # None will indicate special conditions that fire only once, like stun or reduce strength
                self.inflict_damage()

        # game.game.message stuff

    def add_turn(self):
        self.actor.game.ticker.schedule_turn(self.speed, self)

    #########################################################################
    # UTILITY ###############################################################
    #########################################################################
    def get_type(self):
        stat_panel = StatPanel()
        if self.effect_name in stat_panel.panel['elemental']:
            self.panel_group = 'elemental'
        if self.effect_name in stat_panel.panel['modifiers']:
            self.panel_group = 'modifiers'
        if self.effect_name in stat_panel.panel['conditions']:
            self.panel_group = 'conditions'

    def get_real_name(self):
        stat_panel = StatPanel()
        self.effect_real_name = stat_panel.panel[self.panel_group]['key'][self.index]

    def generate_effect(self):  # TODO this is a basic bitch generator, fix it up
        # when you init an effect you can pass a name to get a specific effect type
        if self.effect_name is None:
            stat_panel = StatPanel()
            self.panel_group = random.choice(list(stat_panel.panel))
            name_list = list(stat_panel.panel[self.panel_group])

            self.index = libtcod.random_get_int(0, 0, 1)
            name_list.pop(0)

            self.effect_name = random.choice(name_list)
        self.amount = libtcod.random_get_int(0, 1, 3)

        if self.panel_group == 'conditions':
            self.persist = False  # is this a 1 time persistent stat modifier, like STR down or STUN?
            self.probability = 10  # % chance to trigger effect
            self.duration = 5  # inflicted duration in turns, passed to condition : we'll call it base 5 for now, UG w/ perks
            self.total_duration = self.duration
            self.can_cancel = None  # effect can be cancelled by item or spell - this variable is reserved for that if needed
            self.speed = DEFAULT_EFFECT_SPEED  # declared above ^
            self.max_stack = 1

    def get_color(self):
        stats = StatPanel()
        return stats.get_effect_color(self)
