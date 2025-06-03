__author__ = 'GrishdaFish'

from gEngine.utilities.widget import window_widget, button_widget, text_input_widget, button_group, popups

from game.debug_modules import module_list, dungeon_status, spawning_tool, reload_module

from game.user_interface import help_popup_module

from game import game

from game.spells import spells

from game.classes import skills
from game.classes import warrior_skills

import textwrap


class CharacterCreator(window_widget.WindowWidget):
    def setup(self):
        self.g = game.Game(self.gEngine)
        self.base_width = 25
        self.max_width = 38
        self.buttons = []

        self.warrior_description = True
        self.wizard_description = False
        self.paladin_description = False
        self.ranger_description = False
        self.rogue_description = False

        self.display_description = False

        self.c_name = text_input_widget.TextInputWidget(self, 1, 1, "Name: ", self.max_width)
        self.c_name.default_text = "Player Name"
        self.buttons.append(self.c_name)
        self.exit_button = button_widget.ButtonWidget(self, 1, self.gEngine.h-2, "Finish", self.finish)
        self.buttons.append(self.exit_button)

        self.m_tutorial_group = button_group.ButtonGroupWidget(self, 11, 6, 4, 1)
        self.tutorial_on_button = button_group.GroupButton(self.m_tutorial_group, 1, 0, "Yes")
        self.m_tutorial_group.add_button(self.tutorial_on_button)

        self.c_class_group = button_group.ButtonGroupWidget(self, 1, 4, self.max_width)
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Warrior", self.activate_warrior))
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Wizard", self.activate_wizard))

        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Ranger"))

    def update(self, key, mouse):
        self.gEngine.console_vline(self.con, self.max_width + 2, 1, self.height - 2)
        self.gEngine.console_print(self.con, 1, 3, "Select your class: ")
        self.gEngine.console_print(self.con, 1, 6, "Tutorial? ")
        for button in self.buttons:
            button.run(key, mouse)
        self.c_class_group.run(key, mouse)
        self.m_tutorial_group.run(key, mouse)
        self.description()

    def close(self):
        pass

    def finish(self):
        self.gEngine.modules = []
        self.gEngine.additional_modules = []
        self.gEngine.module_adjust_list = []
        self.g.new_game()
        self.gEngine.add_module(self.g)
        self.create_player()

        d = dungeon_status.DungeonStatus(self.gEngine, self.g, 5, 6, self.gEngine.SCREEN_WIDTH / 2, 7, "Dungeon Status")
        d.deactivate()
        self.gEngine.add_module(d)

        spawn_tool = spawning_tool.SpawningTools(self.gEngine, self.g, 0, 0, 18, 9, "Spawning Tools")
        spawn_tool.setup()
        self.gEngine.add_module(spawn_tool)

        # load this module last
        m = module_list.ModuleList(self.gEngine, self.g, 0, 0, 15, 5, 'Module List')
        self.gEngine.add_module(m)

        r = reload_module.ReloadModule(self.gEngine, x=20, y=0, w=15,h=5,title="Reload Tool")
        r.setup()
        r.activate()
        self.gEngine.add_module(r)

        help_module = help_popup_module.HelpPopup(self.gEngine, self.g, 5, 5, 70, 30, "Help")
        if self.tutorial_on_button.enabled:
            help_module.activate()
        else:
            help_module.deactivate()
        self.gEngine.add_module(help_module)

    def activate_warrior(self):
        self.warrior_description = True
        self.wizard_description = False

        self.display_description = True

    def activate_wizard(self):
        self.wizard_description = True
        self.warrior_description = False

        self.display_description = True

    def description(self):
        text = ""
        if self.warrior_description:
            text = "Melee based class focusing on offense and 2 handed weapons with wide sweeping attacks. " \
                   "High health but low magical ability. Limited scroll usage, but increased torch and lantern duration. " \
                   "Uses heavy armor with less penalties, light armor with no penalties and no armor with bonuses. "
        if self.wizard_description:
            text = "Magic based class that uses torch and lantern power to fuel magical attacks. Can use all wands and " \
                   "scrolls. Can learn spells from scrolls, and permanently cast using lantern power. Unable to use " \
                   "armor, and melee weapons other than staves. Staves are weak single target only weapons."
        if self.paladin_description:
            text = "Paladins are divine warriors that use favor from their chosen god to empower their attacks, smite " \
                   "and blind their foes with divine light."
        if self.ranger_description:
            text = "Rangers are a ranged class focusing on bows and crossbows to keep their foes at range. They have " \
                   "limited access to scrolls but can create makeshift torches out of objects they find in the dungeon."
        if self.rogue_description:
            text = "Rogues are stealthy melee class that focuses on attacking unaware monsters. Masters of shadow, they " \
                   "prefer darkness and have better low light vision than other classes. Has an affinity for wands and " \
                   "other magical objects."
        if self.display_description:
            self.wrapped_text = textwrap.wrap(text, self.max_width)
            l = 0
            for line in self.wrapped_text:
                l += 1
                self.gEngine.console_print(self.con, self.max_width+3, l, line)

    def create_player(self):
        self.g.player.name = self.c_name.text_field

        if self.warrior_description:
            self.create_warrior()
        if self.wizard_description:
            self.create_wizard()
        if self.paladin_description:
            self.create_paladin()
        if self.ranger_description:
            self.create_ranger()
        if self.rogue_description:
            self.create_rogue()

    def create_warrior(self): # TODO: Break this out into its own .py file
        inv = self.g.player.fighter.inventory
        print(self.g.player.name)
        weapon = self.g.build_objects.build_equipment(self.g, 0, 0, name="Great Sword", mat="Iron")
        # weapon.item.equipment.on_hit_effect = spells.explosion # Testing on hit effects

        weapon.item.pick_up(inv)
        chest = self.g.build_objects.build_equipment(self.g, 0, 0, name="plate", mat="Iron")
        chest.item.pick_up(inv)
        head = self.g.build_objects.build_equipment(self.g, 0, 0, name="plate helm", mat="Iron")
        head.item.pick_up(inv)
        for i in range(2):
            t = self.g.build_objects.build_light_source(self.g, 0, 0, "torch")
            t.item.pick_up(inv)
        for x in range(5):
            p = self.g.build_objects.build_potion(self.g, 0, 0, 'healing')
            p.item.pick_up(inv)
        for x in range(20):
            s = self.g.build_objects.build_scroll(self.g, 0, 0, 'fireball')
            s.item.pick_up(inv)
        self.g.player.fighter.money = 200
        self.g.player.fighter.stat.set_stat_base("HP", 75)
        self.g.player.fighter.hp = 75
        self.g.player.fighter.max_consumable_level = 3
        weapon_subtype = "Great Sword"
        self.g.player.fighter.weapon_profs.update({weapon_subtype:self.g.weapon_prof_skills[weapon_subtype]})
        ww = skills.CooldownSkill("Whirlwind", self.g.player, "Whirlwind skill", 3, warrior_skills.whirlwind, self.g, self.gEngine)
        ww.char = "/"
        self.g.player.fighter.active_skills.append(ww)
        #self.g.player.fighter.restricted_weapons = None

    def create_wizard(self):
        pass

    def create_paladin(self):
        pass

    def create_ranger(self):
        pass

    def create_rogue(self):
        pass
