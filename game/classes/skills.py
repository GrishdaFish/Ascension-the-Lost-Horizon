__author__ = 'GrishdaFish'
class Skill:
    def __init__(self, name="", owner=None, description=""):
        self.name = name
        self.owner = owner
        self.description = description
        self.level = 0
        self.level_requirement = 0
        self.required_class = None
        if owner:
            self.gEngine = owner.gEngine
            self.game = owner.game
        else:
            self.gEngine = None
            self.game = None

    def use(self):
        pass

class ActiveSkill(Skill):
    def __init__(self, name="", owner=None, description=""):
        super().__init__(name, owner, description)


class CooldownSkill(ActiveSkill):
    def __init__(self, name="", owner=None, description=""):
        super().__init__(name, owner, description)
        self.cooldown = 0
        self.current_timer = 0

class ResourceSkill(ActiveSkill):
    def __init__(self, name="", owner=None, description=""):
        super().__init__(name, owner, description)
        self.resource_cost = 0
        self.resource_requirement = None

class PassiveSkill(Skill):
    def __init__(self, name="", owner=None, description=""):
        super().__init__(name, owner, description)
