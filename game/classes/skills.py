__author__ = 'GrishdaFish'
import libtcodpy as libtcod
class Skill:
    def __init__(self, name="", owner=None, description=""):
        self.name = name
        self.owner = owner
        self.description = description
        self.level = 0
        self.level_requirement = 0
        self.required_class = None
        self.char = " "
        self.color = libtcod.green

    def use(self):
        pass

class ActiveSkill(Skill):
    def __init__(self, name="", owner=None, description="", game=None, gEngine=None):
        super().__init__(name, owner, description)
        self.game = game
        self.gEngine = gEngine


class CooldownSkill(ActiveSkill):
    def __init__(self, name="", owner=None, description="", cooldown=0, activate=None, game=None, gEngine=None, char=" "):
        """

        :param cooldown: how many turns until reuse
        :param activate: Function pointer to the skill function
        """
        super().__init__(name, owner, description, game, gEngine)
        self.cooldown = cooldown
        self.current_timer = 0
        self.activate = activate
        self.char=char
        self.original_char = char

    def take_turn(self):
        if self.current_timer > 0:
            self.current_timer -= 1
            self.char = str(self.current_timer)
            self.color = libtcod.red
            if self.current_timer == 0:
                self.char = self.original_char
                self.color = libtcod.green

    def use(self):
        if self.current_timer == 0:
            self.activate(self.gEngine, self.game, self.owner)
            self.current_timer = self.cooldown
            self.owner.fighter.cooldown_skills.append(self)
            self.char = str(self.current_timer)
            self.color = libtcod.red
            return True
        else:
            if self.game:
                self.game.message.message("%s skill on cooldown for %d more turns!"%(self.name, self.current_timer), libtcod.red)
            return False



class ResourceSkill(ActiveSkill):
    def __init__(self, name="", owner=None, description="", cost=0, activate=None, game=None, gEngine=None, char=" ", resource="Stamina"):
        super().__init__(name, owner, description, game, gEngine)
        self.resource_cost = cost
        self.resource_requirement = resource
        self.activate = activate
        self.char = char
        self.original_char = char

    def use(self):
        if self.owner.fighter.spend_stamina(self.resource_cost):
            self.activate(self.gEngine, self.game, self.owner)
            return True
        else:
            if self.game:
                self.game.message.message("Not enough %s to use %s!"%(self.resource_requirement, self.name), libtcod.red)
            return False

class PassiveSkill(Skill):
    def __init__(self, name="", owner=None, description=""):
        super().__init__(name, owner, description)
