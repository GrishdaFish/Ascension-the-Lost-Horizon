
class StatPanel:
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
        StatPanel is attached to all instances of fighter to track and adjust
        effects and conditions. Hopefully the design is modular enough to move
        existing stats here and isolate all combat values in one place
    """ """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" """
    def __init__(self):
        # panel will maintain a working reference to all stats
        # DATA MODEL: "Combat Effect name" : [ Damage value, Resistance ]
        #             "Modifiable stat" : value
        #             "Light-based effects" : Not sure yet #TODO  <- consider this
        self.panel = {
            "combat" : {
                # elemental damage/resist
                "Fire"  : [ 0, 0] ,
                "Ice"   : [ 0, 0] ,
                "Stone" : [ 0, 0] ,
                "Storm" : [ 0, 0] ,
                "Holy"  : [ 0, 0] ,
                "Evil"  : [ 0, 0] ,
                # physical damage/resistance
                "Poison" : [ 0, 0] ,
                "Bleed"  : [ 0, 0] ,
                # physical state rate/resistance
                "Stun Rate"    : [ 0, 0] ,
                "Blind Rate"   : [ 0, 0] ,
                "Crit Rate"   : [ 0, 0] ,
                # petrify ?
            },
            "modifiers" : {
                # modifiable base stats
                "HP Modifier"           : 0,
                "Regen Rate"            : 0,
                "Defense Modifier"      : 0,
                "Strength Modifier"     : 0,
                "Constitution Modifier" : 0,
                "Dexterity Modifier"    : 0,
                "Intelligence Modifier" : 0,
                "Speed Modifier"        : 0,
            }
            # dodge, armor, weapon, etc can all be stored here as well
        }

        self.condition_manager = ConditionManager()    # tracks afflicted conditions
        self.combat_effects = []                # tracks actor's equipped combat effects
        self.modifiers = []                     # tracks actor's equipped modifiers

    # called by an effect to register itself
    def apply_effect(self, effect, modifier=False):
        if modifier:
            self.modifiers.append(effect)
            self.panel['modifiers'][effect.stat_effected] += effect.amount
        else:
            self.combat_effects.append(effect)
            self.panel['combat'][effect.stat_effected] += effect.amount

    # called by an effect to un-register itself
    def remove_modifier(self, effect, modifier=False):
        if modifier:
            self.modifiers.remove(effect)
        else:
            self.combat_effects.remove(effect)
        self.panel[effect.stat_effected] -= effect.amount

    # pass it a damage stat to get the resistance to that stat
    def check_resistance(self, stat):
        resistance = stat + 1
        return self.panel[resistance]

    # call as is for bulk damage, pass True for full details
    def return_damage(self, details=False): #TODO determine desired output format
        damage = 0
        damage_detail = []
        if details:
            for mod, val in self.panel:
                if "Damage" in mod:
                    damage_detail.append( [mod, val] )

        else:
            for mod, val in self.panel:
                if "Damage" in mod:
                    damage += val

    # basic to string method to output panel data
    # because of the nature of game's output it seems easier to return an array to iterate over
    def to_string(self):
        info = []
        combat_keys = self.panel['combat'].keys()
        combat_vals = self.panel['combat'].values()
        mod_keys = self.panel['modifiers'].keys()
        mod_vals = self.panel['modifiers'].values()

        for key, val in zip(combat_keys, combat_vals):
            line = "%s D:%d R:%d" % (key, val[0], val[1])
            info.append(line)
        for stat in self.panel['modifiers']:
            line = " %s  %d " % (stat, self.panel['modifiers'][stat])
            info.append(line)
        return info

# manages effects that are active
class ConditionManager:

    def __init__(self):
        self.conditions = []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def remove_condition(self, condition):
        for cond in self.conditions:
            if cond == condition:
                self.conditions.remove(condition)

    def update_conditions(self):
        if len(self.conditions) == 1:
            if self.conditions[0].dead:
                self.conditons.pop(0)
        else:
            for condition in range(len(self.conditions) - 1, 0, -1):
                if self.conditions[condition].dead:
                    self.conditions.pop(condition)

        for condition in self.conditions:
            if not condition.dead:
                condition.update()

    def get_conditions(self):
        return self.conditions


class Condition:
    """
        Conditions are lasting status effects that need to be tracked over multiple turns

    """
    def __init__(self, target, effect):
        self.dead = False
        self.target = target        # Target actor, effected by condition
        self.effect = effect        # instance of effect
        if self.effect.duration:    # will either be a number or None
           pass
           #TODO fix time based to ticker based
            #self.start_time = time.time()
            #self.end_duration = self.time_now + self.effect.duration
        #else:
            #self.start_time = self.effect.duration
            #self.end_duration = self.start_time

    def update(self):
        if not self.dead:
            self.effect.do_effect(); #TODO not an actual function
        #if self.end_duration:
            #if self.time_now > self.end_duration:
                #self.dead = True