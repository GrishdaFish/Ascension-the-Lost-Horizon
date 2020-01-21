__author__ = 'noobspanker'
import os
import sys
import toml
from gEngine.utilities.widget import window_widget, button_widget, text_input_widget, text_button_widget
import tcod as libtcod


class Options(window_widget.WindowWidget):
    """ This is the OPTIONS SELECTION module.
        for default options see options.toml
        for option setup see options.py  """
    def close(self):
        """ close and cleanup children of the module """
        self.gEngine.remove_module(self)
        self.deactivate()
        self.wasd_button.close()
        self.arrows_button.close()
        self.custom_button.close()
        self.save_button.close()
        self.default_button.close()
        self.exit_button.close()

    def setup(self):
        """ let's get this party started """
        self.get_options_from_file()
        self.setup_current_config()
        self.content_setup()

    def update(self, key, mouse):
        """ while doing stuff: pass """
        if not self.collapsed and not self.minimized:
            pass
        # TODO get some stuff going on


    def save(self):
        """ commit changes to options.toml, pass new options to options.py """
        toml_string = toml.dumps(self.content)
        with open('options.toml', mode='w') as w:
            w.writelines(toml_string)
        # TODO pass the new settings to options.py

    def restore_defaults(self):
        """ establish a default setting for each imported setting here """
        # TODO decide what defaults when all options considered
        self.selected_key_set = 'wasd'
        self.set_keymap_keys(self.selected_key_set)

    def get_options_from_file(self):
        """ loads the options settings from options.toml """
        if self.gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        f = open(os.path.join(path, 'options.toml'))
        self.options_file = f.read()
        f.close()

    def setup_current_config(self):
        """ get dict from file content, pull out necessary stuff """
        self.content = toml.loads(self.options_file)
        self.selected_key_set = self.content['game_options']['key_set']
        self.key_options = self.content.get('keys')
        self.set_keymap_keys(self.selected_key_set)

    def set_keymap_keys(self, key_map):
        """ update your keymap settings """
        self.selected_key_set = key_map
        self.content['game_options']['key_set'] = key_map

        self.key_north = self.content['keys'][key_map]['key_north']
        self.key_east = self.content['keys'][key_map]['key_east']
        self.key_south = self.content['keys'][key_map]['key_south']
        self.key_west = self.content['keys'][key_map]['key_west']
        self.key_inventory = self.content['keys'][key_map]['key_inventory']
        self.key_pickups = self.content['keys'][key_map]['key_pickups']
        self.key_help = self.content['keys'][key_map]['key_help']
        self.key_drop = self.content['keys'][key_map]['key_drop']
        self.key_character = self.content['keys'][key_map]['key_character']
        self.key_char_stat = self.content['keys'][key_map]['key_char_stats']

    def set_custom_keys(self, key):
        user_input = None  # TODO create a pop up asking for a character to be entered
        self.content['keys']['custom'][key] = user_input

    def content_setup(self):
        self.gEngine.console_print(self.con, 1, 1, "Key Mapping:")
        # TODO set as button group: ###########################################
        self.wasd_button = button_widget.ButtonWidget(self, 1, 2, "Right Handed", self.set_keymap_keys, ['wasd'])
        self.arrows_button = button_widget.ButtonWidget(self, 14, 2, "Left Handed", self.set_keymap_keys, ['arrows'])
        self.custom_button = button_widget.ButtonWidget(self, 21, 2, "Custom setting", self.set_keymap_keys, ['custom'])
	    #######################################################################

        if self.selected_key_set == 'wasd' or self.selected_key_set == 'arrows': # selected button is wasd or arrows after button group finished
            lines = ["Move Up: " + self.content['keys'][self.selected_key_set]['key_north'],
                     "Move Left:" + self.content['keys'][self.selected_key_set]['key_east'],
                     "Move Down:" + self.content['keys'][self.selected_key_set]['key_south'],
                     "Move Right:" + self.content['keys'][self.selected_key_set]['key_west'],
                     "Open Inventory:" + self.content['keys'][self.selected_key_set]['key_inventory'],
                     "Pick up items:" + self.content['keys'][self.selected_key_set]['key_pickups'],
                     "Open help screen:" + self.content['keys'][self.selected_key_set]['key_help'],
                     "Drop item:" + self.content['keys'][self.selected_key_set]['key_drop'],
                     "Open character stats:" + self.content['keys'][self.selected_key_set]['key_character'],
                     "*Bonus* menu:" + self.content['keys'][self.selected_key_set]['key_char_stat']
                    ]
            self.print_lines(lines, y=3)
        if self.selected_key_set == 'custom':  # if selected button is custom we need each one to be clickable and call self.set_custom_keys passing in the key
            lines = ["Move Up: " + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_north'], self.set_custom_keys, ['key_north']),
                "Move Left:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_east'],
                 "Move Down:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_south'],
                 "Move Right:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_west'],
                 "Open Inventory:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_inventory'],
                 "Pick up items:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_pickups'],
                 "Open help screen:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_help'],
                 "Drop item:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_drop'],
                 "Open character stats:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_character'],
                 "*Bonus* menu:" + text_button_widget.TextButtonWidget(self, 1, 3, self.content['keys'][self.selected_key_set]['key_char_stat']
                ]

        self.save_button = button_widget.ButtonWidget(self, self.width / 2, 4, "Save and exit", self.save)
        self.default_button = button_widget.ButtonWidget(self, self.width / 2, 5, "Restore defaults",
                                                         self.restore_defaults)
        self.exit_button = button_widget.ButtonWidget(self, self.width / 2, 6, "Exit without save", self.close)

    def print_lines(self, y=0, custom=False):