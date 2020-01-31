__author__ = 'noobspanker'
import os
import sys
import toml
from gEngine.utilities.widget import window_widget, button_widget, text_input_widget, button_group
import tcod as libtcod

# TODO This popup needs to be able to tell if the key is already mapped to something else and deal with it
#       we could unset the previously mapped key, or just cancel mapping the new key with error message
class KeySelectPopup(window_widget.WindowWidget):
    """ Popup used to grab the new key to use from input """
    def close(self):
        """ take out the trash """
        self.gEngine.remove_module(self)
        self.deactivate()

    def update(self, key, mouse):
        """ do my thing til input received """
        self.gEngine.console_print(self.con, int(self.width/2 - (len(self.message) / 2)), 2, self.message)
        self.gEngine.console_print(self.con, int(self.width/2 - (len(self.prompt) / 2)), 4, self.prompt)
        if key.c or key.vk or mouse.lbutton or mouse.rbutton:
            if self.keyset == 'wasd' or self.keyset =='arrows':
                self.close()
            if self.keyset == 'custom':
                if key.c and key.c > 10:
                    self.owner.get_popup_input(self.key_name, chr(key.c))
                    self.close()

    def setup(self, op_module, nice_name, key_name, selected_keyset):
        """ pass in the options module so we can pass the input back to its function
            key_name is the toml name i.e. key_help
            keyset is your current game_options: key_set selection """

        self.owner = op_module
        self.keyset = selected_keyset
        self.key_name = key_name
        if selected_keyset == 'wasd' or selected_keyset == 'arrows':
            self.message = "Please select 'Custom' Key Map to set your custom keys."
            self.prompt = "Press any key to continue."
        if selected_keyset == 'custom':
            self.message = "Press a key to re-map:" + nice_name
            self.prompt = "Press escape to cancel."

class OptionsModule(window_widget.WindowWidget):
    """ This is the OPTIONS SELECTION module.
        for default/saved options see options.toml
        for options setup see options.py
        for instantiation see esc_menu.py and main_menu.py"""
    def close(self):
        """ close and cleanup children of the module """
        self.gEngine.remove_module(self)
        self.deactivate()
        for button in self.widgets:
            button.close()
        for button in self.keymap_widgets:
            button.close()
        if self.key_popup:
            self.key_popup.close()

    def setup(self):
        """ let's get this party started """
        self.width = self.gEngine.SCREEN_WIDTH
        self.height = self.gEngine.SCREEN_HEIGHT
        self.gEngine.console_remove_console(self.con)
        self.con = self.gEngine.console_new(self.width, self.height)
        self.title_x_position = self.width / 2 - (len(self.title) / 2)

        self.key_popup = None
        self.widgets = []
        self.widget_groups = []
        self.keymap_widgets = []
        self.get_options_from_file()
        self.setup_current_config()
        self.dynamic_content_setup()
        self.static_content_setup()

    def update(self, key, mouse):
        """ while doing stuff: pass """
        if not self.collapsed and not self.minimized:
            self.print_static_content()
            for widgets in self.widget_groups:
                if self.active:
                    widgets.run(key, mouse)
            for widget in self.widgets:
                if self.active:
                    widget.run(key, mouse)
            for buttons in self.keymap_widgets:
                if self.active:
                    buttons.run(key, mouse)

    ############################################################################################
    # Setup  ###################################################################################
    ############################################################################################
    def get_options_from_file(self):
        """ loads the options settings from options.toml """
        #if self.gEngine.RELEASE:
         #   path = getattr(sys, "_MEIPASS", ".")
        #else:
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
        self.key_char_stat = self.content['keys'][key_map]['key_char_stat']
        self.key_perks = self.content['keys'][key_map]['key_perks']
        self.dynamic_content_setup()

    ############################################################################################
    # Button Functions  ########################################################################
    ############################################################################################
    def save(self):
        """ commit changes to options.toml, pass new options to options.py """
        toml_string = toml.dumps(self.content)
        with open('options.toml', mode='w') as w:
            w.writelines(toml_string)
        self.gEngine.options.reload_options()
        self.close()

    def restore_defaults(self):
        """ establish a default setting for each imported setting here """
        # TODO decide what defaults when all options considered
        self.selected_key_set = 'wasd'
        self.set_keymap_keys(self.selected_key_set)

    ############################################################################################
    # Popup functions ##########################################################################
    ############################################################################################
    def get_popup_input(self, key_name, key_input):
        """ function called by the KeySelectPopup to return the user input """
        self.content['keys'][self.selected_key_set][key_name] = key_input
        self.set_keymap_keys(self.selected_key_set)
        self.key_popup = None

    def set_custom_keys(self, nice_name, key_name):
        """ calls the popup when you click on a mappable key, popup provides message for unmappable keysets """
        popup_width = 60
        popup_height = 7
        self.key_popup = KeySelectPopup(self.gEngine, None, int(self.width / 2 - (popup_width / 2)), self.height / 3, popup_width, popup_height, "Remap Key")
        self.key_popup.setup(self, nice_name, key_name, self.selected_key_set)
        self.gEngine.add_module(self.key_popup)

    ############################################################################################
    # WARNING: Ugly UI bullshit forthcoming ####################################################
    ############################################################################################
    def static_content_setup(self):
        """ define ui shit that doesnt change over the life of the module """
        self.keyset_button_group = button_group.ButtonGroupWidget(self, int(self.width / 5), 2, 55, 1)
        self.keyset_button_group.add_button(button_group.GroupButton(self.keyset_button_group, 1, 0, "Right Handed", self.set_keymap_keys, ['wasd']))
        self.keyset_button_group.add_button(button_group.GroupButton(self.keyset_button_group, 1, 0, "Left Handed", self.set_keymap_keys, ['arrows']))
        self.keyset_button_group.add_button(button_group.GroupButton(self.keyset_button_group, 1, 0, "Custom setting", self.set_keymap_keys, ['custom']))
        self.widget_groups.append(self.keyset_button_group)
        for button in self.keyset_button_group.buttons:
            if button.original_label == "Right Handed" and self.selected_key_set == "wasd":
                button.enabled = True
                button.active = True
            elif button.original_label == "Left Handed" and self.selected_key_set == "arrows":
                button.enabled = True
                button.active = True
            elif button.original_label == "Custom setting" and self.selected_key_set == "custom":
                button.enabled = True
                button.active = True

        self.save_button = button_widget.ButtonWidget(self, 7, 15, "Save and exit", self.save)
        self.default_button = button_widget.ButtonWidget(self, 25, 15, "Restore defaults", self.restore_defaults)
        self.exit_button = button_widget.ButtonWidget(self, 45, 15, "Exit without save", self.close)

        self.widgets.append(self.save_button)
        self.widgets.append(self.default_button)
        self.widgets.append(self.exit_button)

        # libtcod.sys_save_screenshot()

    def dynamic_content_setup(self):
        """ define ui shit that will be manipulated over the life of the module """
        if len(self.keymap_widgets) > 0:
            for button in self.keymap_widgets:
                if self.active:
                    button.close()
        self.keymap_widgets.clear()

        self.keymap_widgets.append(button_widget.TextButtonWidget(self, int(self.width/5 - 1), 4, self.key_north, self.set_custom_keys, ['Move Up', 'key_north']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, int(self.width/5 + 1), 6, self.key_east, self.set_custom_keys, ['Move Right', 'key_east']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, int(self.width/5 - 1), 8, self.key_south, self.set_custom_keys, ['Move Down', 'key_south']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, int(self.width/5 - 3), 6, self.key_west, self.set_custom_keys, ['Move Left', 'key_west']))

        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 29, 5, "Inventory: ".ljust(12) + self.key_inventory, self.set_custom_keys, ['Inventory', 'key_inventory']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 55, 5, "Pick up: ".ljust(12) + self.key_pickups, self.set_custom_keys, ['Pick Up', 'key_pickups']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 29, 6, "Help: ".ljust(12) + self.key_help, self.set_custom_keys, ['Help', 'key_help']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 55, 6, "Drop item: ".ljust(12) + self.key_drop, self.set_custom_keys, ['Drop Item', 'key_drop']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 29, 7, "Character: ".ljust(12) + self.key_character, self.set_custom_keys, ['Character', 'key_character']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 29, 8, "*Bonus* menu:".ljust(12) + self.key_char_stat, self.set_custom_keys, ['Bonus Menu', 'key_char_stat']))
        self.keymap_widgets.append(button_widget.TextButtonWidget(self, 29, 9, "Perks: ".ljust(12) + self.key_perks, self.set_custom_keys, ['Perks', 'key_perks']))

    def print_static_content(self):
        """ helper function to keep my update fucntion clean """
        # if gimmie_da_hline(): dev.uncomment_next_line(num_lines=2)
        # self.gEngine.console_hline(self.con, 1, 3, self.width, flag=libtcod.BKGND_COLOR_BURN) # because FIRE
        # self.gEngine.console_hline(self.con, 1, 12, self.width, flag=libtcod.BKGND_COLOR_BURN) # todo calculate magic # 12: get y depth of menu items
        self.gEngine.console_print(self.con, 1, 1, "Key Mapping:")
        self.gEngine.console_print(self.con, 3, 5, "Movement:")
        self.gEngine.console_print(self.con, 22, 5, "Menus:")
        self.gEngine.console_print(self.con, 22, 4, "Game Menu: Esc")
        self.gEngine.console_print(self.con, 45, 5, "Actions:")
        self.gEngine.console_print(self.con, 55, 7, "Go up: <")
        self.gEngine.console_print(self.con, 55, 8, "Go Down: >")
        self.gEngine.console_print(self.con, int(self.width / 5 - 1), 5, chr(libtcod.CHAR_TEEN))
        self.gEngine.console_print(self.con, int(self.width / 5 - 2), 6,
                                   chr(libtcod.CHAR_TEEW) + '@' + chr(libtcod.CHAR_TEEE))
        self.gEngine.console_print(self.con, int(self.width / 5 - 1), 7, chr(libtcod.CHAR_TEES))