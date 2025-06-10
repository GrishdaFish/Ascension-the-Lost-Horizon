__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import text_input_widget
from gEngine.utilities.widget import button_group
from gEngine.utilities.widget import popups

from game.classes import skills

import textwrap

import tcod as libtcod



class SkillScreen(window_widget.WindowWidget):
    def setup(self, game=None):
        if not self.game:
            if game:
                self.game = game
        self.buttons = []
        self.hovered_skill = None
        #self.game = game
        self.player = self.game.player
        self.skill_info_x_offset = self.width/2
        self.skill_description_y_offset = self.height/2
        self.fighter = self.player.fighter
        self.skills = []
        #if not skills:
        self.skills.extend(self.game.player.fighter.active_skills)
        self.skills.extend(self.game.player.fighter.passives)
        i = 3
        for skill in self.skills:
            b = SkillButton(self, 2, i, skill.name, None)
            b.setup(skill)
            self.buttons.append(b)
            i+=1
        self.buttons.append(button_widget.ButtonWidget(self, 15, self.height-2, "Choose New Skill", self.new_skill_screen))
        self.buttons.append(button_widget.ButtonWidget(self, 2, self.height-2, "Close", self.deactivate))

    def update(self, key, mouse):
        if self.active:
            if key.vk == libtcod.KEY_ESCAPE:
                self.deactivate()
                return
            self.gEngine.console_print_frame(self.con, 1, 1, self.width/2-1, self.height-2, True, "Learned Skills")
            self.gEngine.console_print_frame(self.con, self.skill_info_x_offset, 1, self.width / 2 - 1, self.height/2-1 , True, "Skill Info")
            self.gEngine.console_print_frame(self.con, self.skill_info_x_offset, self.skill_description_y_offset, self.width / 2 - 1, self.height/2 , True, "Skill Description")
            for button in self.buttons:
                button.run(key, mouse)

            self.draw_skill_info()
            self.draw_skill_description()
            if self.game.player.fighter.unused_skill_points > 0:
                col = libtcod.green
            else:
                col = libtcod.red
            s = self.gEngine.color_text(str(self.game.player.fighter.unused_skill_points), col)

            self.gEngine.console_print(self.con, 2, self.height-3, "Available Skill points: %s"%s)

    def deactivate(self):
        self.active = False
        self.game.activate()

    def draw_skill_info(self):
        skill_name = ""
        skill_level = ""
        if self.hovered_skill:
            skill_name = self.gEngine.color_text(self.hovered_skill.name, libtcod.grey)
            skill_level = self.gEngine.color_text(self.hovered_skill.level, libtcod.grey)
        self.gEngine.console_print(self.con, self.skill_info_x_offset+1, 2, "Skill Name: %s"%skill_name)
        self.gEngine.console_print(self.con, self.skill_info_x_offset + 1, 3, "Skill Level: %s" % skill_level)

        if isinstance(self.hovered_skill, skills.CooldownSkill):
            cooldown = self.gEngine.color_text(str(self.hovered_skill.cooldown), libtcod.grey)
            self.gEngine.console_print(self.con, self.skill_info_x_offset+1, 4, "Cooldown turns: %s"%cooldown)

        elif isinstance(self.hovered_skill, skills.ResourceSkill):
            cost = self.gEngine.color_text(str(self.hovered_skill.resource_cost), libtcod.grey)
            resource = self.gEngine.color_text(self.hovered_skill.resource_requirement, libtcod.grey)
            resource.upper()
            self.gEngine.console_print(self.con, self.skill_info_x_offset + 1, 4, "Cost: %s %s" %(cost, resource))


    def draw_skill_description(self):
        skill_desc = ""
        if self.hovered_skill:
            skill_desc = self.hovered_skill.description
        wrapped_text = textwrap.wrap(skill_desc, self.width/2 - 2)
        l=2
        for line in wrapped_text:
           line = self.gEngine.color_text(line, libtcod.dark_grey)
           self.gEngine.console_print(self.con, self.skill_info_x_offset+1, self.skill_description_y_offset+l, line)
           l+=1

    def new_skill_screen(self):
        self.skills = []
        self.buttons = []
        self.skills.extend(self.game.active_skills)
        self.skills.extend(self.game.passive_skills)
        i = 3
        for skill in self.skills:
            b = LearnSkillButton(self, 2, i, skill.name, None)
            b.setup(skill)
            self.buttons.append(b)
            i += 1

        self.buttons.append(button_widget.ButtonWidget(self, 2,  self.height - 2, "Close", self.deactivate))
        self.buttons.append(button_widget.ButtonWidget(self, 12, self.height - 2, "Back",  self.setup))

class SkillButton(button_widget.ButtonWidget):
    def setup(self, skill):
        self.skill = skill
        self.function = self.select
        self.background_color = libtcod.black

    def update(self, key, mouse):
        if self.mouse_is_in_console(mouse):
            self.parent.hovered_skill = self.skill
            self.background_color = libtcod.lighter_grey
        else:
            self.background_color = libtcod.black

    def select(self):
        self.parent.hovered_skill = self.skill

class LearnSkillButton(SkillButton):
    def select(self):
        if self.parent.fighter.unused_skill_points > 0:
            self.popup = popups.Confirm(self.gEngine, x=0, y=self.parent.height/2, w=5, h=5, title="Confirm Spend Skill Point")
            self.popup.setup("Do you want to spend a skill point on %s"%self.skill.name, callback=self.learn_skill, ok="Yes", cancel="No")
            self.popup.x = self.popup.x + self.popup.width / 2
            self.popup.activate()
            self.gEngine.bring_module_to_front(self.popup)
        else:
            popup = popups.Alert(self.gEngine, x=self.parent.width/2, y=self.parent.height /2, w=26, h=5,title="Not Enough Skill Points!")
            popup.setup("You do not have enough skill points to learn this skill!")
            popup.x = popup.x - popup.width /2
            popup.activate()
            self.gEngine.bring_module_to_front(popup)

    def learn_skill(self, callback):
        if callback:
            self.parent.fighter.unused_skill_points -= 1
            if isinstance(self.skill, skills.PassiveSkill):
                self.parent.fighter.passives.append(self.skill)
                self.parent.game.passive_skills.remove(self.skill)
            else:
                self.parent.fighter.active_skills.append(self.skill)
                self.parent.game.active_skills.remove(self.skill)
            self.parent.skills.remove(self.skill)
            self.parent.new_skill_screen()
            self.popup.close()
        else:
            self.popup.close()
            return