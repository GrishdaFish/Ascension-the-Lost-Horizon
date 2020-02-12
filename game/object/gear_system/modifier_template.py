from game.object.effects import Effect


class ModifierTemplate:
    def __init__(self, name, owner):
        self.name = name  # key from GearPanel.damage_types
        self.owner = owner
        self.level = 1
        self.xp = 0
        # store stats as effects to compare / remove / replace
        self.mod_effects = []
        # modifiable stats
        self.damage_mod = 0
        self.crit_rate_mod = 0
        self.accuracy_mod = 0
        self.block_mod = 0
        self.defense_mod = 0
        self.parry_mod = 0
        self.evasion_mod = 0
        self.str_mod = 0
        self.con_mod = 0
        self.dex_mod = 0
        self.int_mod = 0

    def activate(self):
        """ create an effect for each stat and add to the player after it levels up, or call directly """
        if self.mod_effects:
            self.mod_effects.clear()

        if self.damage_mod:
            self.push_effect("Damage", self.damage_mod)
        if self.crit_rate_mod:
            self.push_effect("Crit Rate", self.crit_rate_mod)
        if self.accuracy_mod:
            self.push_effect("Accuracy", self.accuracy_mod)
        if self.block_mod:
            self.push_effect("Block", self.block_mod)
        if self.defense_mod:
            self.push_effect("Defense", self.defense_mod)
        if self.parry_mod:
            self.push_effect("Parry", self.parry_mod)
        if self.evasion_mod:
            self.push_effect("Evasion", self.evasion_mod)
        if self.str_mod:
            self.push_effect("Strength", self.str_mod)
        if self.con_mod:
            self.push_effect("Constitution", self.con_mod)
        if self.dex_mod:
            self.push_effect("Dexterity", self.dex_mod)
        if self.int_mod:
            self.push_effect("Intelligence", self.int_mod)

        for fx in self.mod_effects:
            fx.activate_effect(self.owner)

    def push_effect(self, name, amount):
        """ helper function for filling the effect array in activate """
        fx = Effect(None, name, amount)
        fx.index = 1  # makes it a modifier
        self.mod_effects.append(fx)

    def deactivate(self):
        """ deactivates all the old effects and empties the array on level up, or when no longer in use """
        for fx in self.mod_effects:
            fx.deactivate_effect()
        self.mod_effects.clear()


class DamageType(ModifierTemplate):
    """ contains a modifier for each player stat based on their equipped damage type """

    def check_for_level_up(self):
        """ check exp, do level up """
        # TODO BALANCING just calling this 1000 xp / lvl for now,
        if self.xp >= self.level*1000:
            self.xp -= self.level*1000
            self.level += 1
            self.level_up()

    def level_up(self):
        """ very basic to begin with, we can balance here, and also unlock different stats per type via perks, etc. """
        if self.mod_effects:
            self.deactivate()

        if self.name == 'Shield':
            self.defense_mod += 1
            self.block_mod += 1
            self.con_mod += 1
        if self.name == 'Slash':
            self.parry_mod += 1
            self.crit_rate_mod += 1
            self.dex_mod += 1
        if self.name == 'Smash':
            self.damage_mod += 1
            self.defense_mod += 1
            self.str_mod += 1
        if self.name == 'Stab':
            self.accuracy_mod += 1
            self.evasion_mod += 1
            self.int_mod += 1

        self.activate()
