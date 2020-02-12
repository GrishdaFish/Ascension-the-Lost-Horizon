import copy


class Perk:
    """ Perk base class provides all the necessary global features, at minimum you must override activate """
    def __init__(self, owner, weapon_type, branch, height, max_level, trigger):
        self.owner = owner
        self.weapon_type = weapon_type
        self.branch = branch
        self.height = height
        self.level = 0
        self.max_level = max_level
        self.threat = 1
        self.description = None
        #
        self.trigger = trigger
        self.is_active = False  # active effects, not just active skills (but also active skills :D)
        self.is_locked_out = False  # for top path lockout tracking

    def get_threat(self):
        return self.threat

    def set_description(self, description):
        """ rather than having a big stupid ass string for every constructor we can use this to pass each skill its
            description from another source (dict, toml, etc.) en mass, ex post-facto,
            this should also be where unified output formatting (flavor country) is done """
        self.description = description

    def level_up(self):
        """ simply checks for max level and increases """
        if self.max_level > self.level:
            self.level += 1
            self.apply_level_up()
            return True
        return False

    def lockout_skill(self):
        """ locks out an upper tree skill """
        self.is_locked_out = True

    def apply_level_up(self):
        """ override to generate unique level up procedure """
        pass

    def activate(self):
        """ override to generate an activate procedure """
        pass

    def deactivate(self):
        """ override to deactivate """
        pass

    def update(self, stuff):
        """ under consideration for active skill duration tracking """
        pass

