__author__ = 'GrishdaFish'
from gEngine.utilities.widget import window_widget, button_widget, text_input_widget, button_group, popups
from game.debug_modules import module_list, dungeon_status, spawning_tool
from game.user_interface import help_popup_module
from game import game
import textwrap


class CharacterCreator(window_widget.WindowWidget):
    def setup(self):
        self.base_width = 25
        self.max_width = 38
        self.buttons = []
        self.f_description = False
        self.w_description = False
        self.display_description = False

        self.c_name = text_input_widget.TextInputWidget(self, "Name: ", 1, 1, self.max_width)
        self.c_name.default_text = "Player Name"
        self.buttons.append(self.c_name)
        self.exit_button = button_widget.ButtonWidget(self, 1, self.gEngine.h-2, "Finish", self.finish)
        self.buttons.append(self.exit_button)


        self.c_class_group = button_group.ButtonGroupWidget(self, 1, 4, self.max_width)
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Fighter", self.activate_fighter))
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Wizard", self.activate_wizard))
        self.c_class_group.add_button(button_group.GroupButton(self.c_class_group, 1, 0, "Ranger"))

    def update(self, key, mouse):
        self.gEngine.console_vline(self.con, self.max_width + 2, 1, self.height - 2)
        self.gEngine.console_print(self.con, 1, 3, "Select your class: ")
        for button in self.buttons:
            button.run(key, mouse)
        self.c_class_group.run(key, mouse)
        self.description()

    def close(self):
        pass

    def finish(self):
        self.gEngine.modules = []
        self.gEngine.additional_modules = []
        self.gEngine.module_adjust_list = []
        g = game.Game(self.gEngine)
        g.new_game()
        self.gEngine.add_module(g)

        d = dungeon_status.DungeonStatus(self.gEngine, g, 5, 6, self.gEngine.SCREEN_WIDTH / 2, 7, "Dungeon Status")
        d.deactivate()
        self.gEngine.add_module(d)

        spawn_tool = spawning_tool.SpawningTools(self.gEngine, g, 0, 0, 18, 9, "Spawning Tools")
        spawn_tool.setup()
        self.gEngine.add_module(spawn_tool)

        # load this module last
        m = module_list.ModuleList(self.gEngine, g, 0, 0, 15, 5, 'Module List')
        self.gEngine.add_module(m)

        help_module = help_popup_module.HelpPopup(self.gEngine, g, 5, 5, 70, 30, "Help")
        self.gEngine.add_module(help_module)

    def activate_fighter(self):
        self.f_description = True
        self.w_description = False

        self.display_description = True

    def activate_wizard(self):
        self.w_description = True
        self.f_description = False

        self.display_description = True

    def description(self):
        text = ""
        if self.f_description:
            text = "Melee based class focusing on offense and 2 handed weapons with wide sweeping attacks. " \
                   "High health but low magical ability. Limited scroll usage, but increased torch and lantern duration. " \
                   "Uses heavy armor with less penalties, light armor with no penalties and no armor with bonuses. "
        if self.w_description:
            text = "Magic based class that uses torch and lantern power to fuel magical attacks. Can use all wands and " \
                   "scrolls. Can learn spells from scrolls, and permanently cast using lantern power. Unable to use " \
                   "armor, and melee weapons other than staves. Staves are weak single target only weapons."
        if self.display_description:
            self.wrapped_text = textwrap.wrap(text, self.max_width)
            l = 0
            for line in self.wrapped_text:
                l += 1
                self.gEngine.console_print(self.con, self.max_width+3, l, line)
