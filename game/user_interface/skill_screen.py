__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import text_input_widget
from gEngine.utilities.widget import button_group
from gEngine.utilities.widget import popups

import libtcodpy as libtcod

class SkillScreen(window_widget.WindowWidget):
    def setup(self, game):
        self.buttons = []
        self.hovered_skill = None
        self.game = game
        self.player = game.player
        self.fighter = self.player.fighter
        self.skills = self.fighter.active_skills
        self.skills.extend(self.fighter.passives)
        self.skills.extend(self.fighter.cooldown_skills)
        i = 2
        for skill in self.skills:
            b = SkillButton(self, 2, i, skill.name, None)
            b.setup(skill)
            self.buttons.append(b)
            i+=1

    def update(self, key, mouse):
        self.gEngine.console_print_frame(self.con, 1, 1, self.width/2-1,self.height-2, True)
        self.gEngine.console_print_frame(self.con, self.width / 2, 1, self.width / 2 - 2, self.height/2-1 , True)
        self.gEngine.console_print_frame(self.con, self.width / 2, self.height/2, self.width / 2 - 2, self.height/2 , True)
        for button in self.buttons:
            button.run(key, mouse)

    def deactivate(self):
        self.active = False
        self.game.activate()

class SkillButton(button_widget.TextButtonWidget):
    def setup(self, skill):
        self.skill = skill
        self.function = self.select
    def update(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            self.parent.hovered_skill = self.skill
            self.background_color = libtcod.lighter_grey
        else:
            self.background_color = libtcod.black

    def select(self):
        self.parent.hovered_skill = self.skill