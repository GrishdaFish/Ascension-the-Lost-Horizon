import tcod as libtcod

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
                # elemental damage/resist/display color
                "Fire": [0, 0, libtcod.red],
                "Ice": [0, 0, libtcod.light_blue],
                "Stone": [0, 0, libtcod.grey],
                "Storm": [0, 0, libtcod.light_purple],
                "Holy": [0, 0, libtcod.gold],
                "Evil": [0, 0, libtcod.dark_grey],
                # physical damge/resistance
                "Poison": [0, 0, libtcod.green],
                "Bleed": [0, 0, libtcod.dark_crimson],
                # physical stae rate/resistance
                "Crit Rate": [0, 0, libtcod.light_grey],
                # petrify ?
            },
            "modifiers" : {
                # modifiable base stats
                "HP": 0,
                "Regen": 0,
                "Defense": 0,
                "Strength": 0,
                "Constitution": 0,
                "Dexterity": 0,
                "Intelligence": 0,
                "Speed": 0,
            },
            "conditions" : {
                # conditions the actor can cause / resist [damage, resistance, rate, display color]
                "Burn":  [0, 0, 0, libtcod.red],
                "Freeze":  [0, 0, 0, libtcod.light_blue],
                "Tremor":  [0, 0, 0, libtcod.grey],
                "Shock":  [0, 0, 0, libtcod.light_purple],
                "Smite":  [0, 0, 0, libtcod.gold],
                "Corrupt":  [0, 0, 0, libtcod.dark_grey],
                "Plague":  [0, 0, 0, libtcod.green],
                "Gash":  [0, 0, 0, libtcod.dark_crimson],
                "Stun": [0, 0, 0, libtcod.orange],
                "Blind": [0, 0, 0, libtcod.darkest_grey],
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
            self.panel['modifiers'][effect.effect_name] += effect.amount
        else:
            self.combat_effects.append(effect)
            self.panel['combat'][effect.effect_name][0] += effect.amount # 0 index calls damage, hard coded for testing

    # called by an effect to un-register itself
    def remove_effect(self, effect, modifier=False):
        if modifier:
            self.modifiers.remove(effect)
        else:
            self.combat_effects.remove(effect)
        self.panel['combat'][effect.effect_name][0] -= effect.amount  # 0 index calls damage, hard coded for testing

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
        #prepare a big dumb ass string to output
        line = " Combat Effects:"
        info.append(line)
        line = "Effect: Damage / Resist"
        info.append(line)
        # format combat effects
        for key, val in zip(self.panel['combat'].keys(), self.panel['combat'].values()):
            line = "%s:  %d / %d" % (key, val[0], val[1])
            info.append(line)
        line = ""
        info.append(line)
        line = " Modifiers:"
        info.append(line)
        # format modifiers
        for stat in self.panel['modifiers']:
            line = "%s:  %d " % (stat, self.panel['modifiers'][stat])
            info.append(line)
        line = ""
        info.append(line)
        line = " Conditions:"
        info.append(line)
        line = "Effect: Damage / Resist / Trigger %"
        info.append(line)
        # format conditions
        for stat, val in zip(self.panel['conditions'].keys(), self.panel['conditions'].values()):
            line = "%s:  %d / %d / %d " % (stat, val[0], val[1], val[2])
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