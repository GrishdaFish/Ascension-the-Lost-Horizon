import tcod as libtcod
from game import game
from game import dev_mode
from game.debug_modules import module_list
from game.debug_modules import dungeon_status
from game.debug_modules import spawning_tool
from game.modules import login_module, options_module, inventory_module
from gEngine.utilities.user_interface.menu import Menus
from gEngine.utilities.widget import button_widget
from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_group
import os
import sys
from gEngine import gEngine as _gEngine
import time
import webbrowser
from gEngine import custom_font


class MainMenu:
    def __init__(self, gEngine):
        self.gEngine = gEngine
        self.active = True
        self.con = 0  # self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        if _gEngine.RELEASE:
            path = getattr(sys, "_MEIPASS", ".")
        else:
            path = sys.path[0]
        path = os.path.join(path, 'content')

        self.first = True
        self.intro_done = False
        self.logo_done = False
        self.letter_index = 0
        self.studio_name = 'Critical Miss Studios'
        self.name_done = False
        self.print_name = ''
        self.lerp_value = 0.0
        self.lerp_amount = 0.087

        self.menu_fade = True
        self.menu_fade_amount = 0.05
        self.menu_fade_value = 0.0

        self.menu_widget = MenuWidget(self.gEngine, None, self.gEngine.SCREEN_WIDTH / 2 - 12,
                                      self.gEngine.SCREEN_HEIGHT / 2 - 7, 24, 12, "Main Menu")

        self.menu_widget.setup()
        self.menu_widget.deactivate()

    def activate(self):
        self.active = True
        self.first = True
        self.intro_done = False
        self.logo_done = False
        self.letter_index = 0
        self.studio_name = 'Critical Miss Studios'
        self.name_done = False
        self.print_name = ''
        self.lerp_value = 0.0
        self.lerp_amount = 0.087

        self.menu_fade = True
        self.menu_fade_amount = 0.05
        self.menu_fade_value = 0.0

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()

    def run(self, key, mouse):
        if self.first:
            self.gEngine.log_open_block("Main menu running...")
            self.first = False
            login = login_module.LoginMenu(self.gEngine, None, self.gEngine.SCREEN_WIDTH / 4,
                                           self.gEngine.SCREEN_HEIGHT / 4,
                                           25, 7, "Login")
            login.setup()
            self.gEngine.add_module(login)
            self.gEngine.add_module(self.menu_widget)
            return

        self.gEngine.console_clear(self.con)
        self.gEngine.console_clear(0)

        if not self.intro_done:
            img = "game logo fade"
            self.intro_done = self.gEngine.animation_draw_animation(img, 0, 0, 0)
        else:
            img = "game logo flicker"
            self.gEngine.animation_draw_animation(img, 0, 0, 0)

        if self.logo_done:
            if self.letter_index < len(self.studio_name):
                self.print_name += self.studio_name[self.letter_index]
            else:
                self.name_done = True
            self.letter_index += 1

        self.logo_done = self.gEngine.animation_draw_animation("title logo", 0, 0, 29)

        r, g, b = libtcod.color_lerp(libtcod.light_flame, libtcod.dark_flame, self.lerp_value)
        if self.name_done:
            self.lerp_value += self.lerp_amount
            if self.lerp_value < 0.087:
                self.lerp_amount = 0.087
            if self.lerp_value > 0.913:
                self.lerp_amount = -0.087

        self.gEngine.console_set_default_foreground(0, r, g, b)
        self.gEngine.console_print(0, int(self.gEngine.SCREEN_WIDTH / 2 - 11),
                                   int(self.gEngine.SCREEN_HEIGHT - 15),
                                   self.print_name)

        self.gEngine.console_set_default_background(0, 0, 0, 0)
        if self.intro_done:
            if self.menu_fade:
                if self.menu_fade_value < 1.0:
                    self.menu_fade_value += self.menu_fade_amount
                else:
                    # menu_fade_value = 1.0
                    self.menu_fade = False

        if not self.gEngine.get_module_status("LoginMenu"):
            # TODO REFACTOR this to prevent constant creation of new buttons
            if self.gEngine.player_id:
                logout = False
                for button in self.menu_widget.buttons:
                    if button.original_label == "Logout":
                        logout = True
                        break

                if not logout:
                    for button in self.menu_widget.buttons:
                        if button.original_label == "Login":
                            button.close()
                            self.menu_widget.buttons.remove(button)
                            break

                    self.menu_widget.buttons.append(LogoutButton(self.menu_widget, 1, 6, "Logout", None))
            elif not self.gEngine.player_id:
                login = False
                for button in self.menu_widget.buttons:
                    if button.original_label == "Login":
                        login = True
                        break
                if not login:
                    for button in self.menu_widget.buttons:
                        if button.original_label == "Logout":
                            button.close()
                            self.menu_widget.buttons.remove(button)
                            break
                    self.menu_widget.buttons.append(Login(self.menu_widget, 1, 6, "Login", None))

            self.menu_widget.activate()


class MenuWidget(window_widget.WindowWidget):
    def close(self):
        for button in self.buttons:
            button.close()
        self.deactivate()
        self.gEngine.remove_module(self)
        # exit(6942069)  # you can't stop me lmao

    def setup(self):
        self.buttons = []

        self.buttons.append(NewGame(self, 1, 1, "New Game", None))
        self.buttons.append(LoadGame(self, 1, 2, "Continue Last Game", None))
        self.buttons.append(Options(self, 1, 3, "Options", None))
        self.buttons.append(CloseGame(self, 1, 4, "Quit", None))
        self.buttons.append(DevMode(self, 1, 5, "Developer Mode", None))
        self.buttons.append(DiscordButton(self, 1, 7, "Join Discord", None))

        self.button_group = button_group.ButtonGroupWidget(self, 1, 8, 5, 1)
        self.button_group.add_button(button_group.GroupButton(self.button_group, 1, 0, chr(custom_font.CHAR_ARROW_N)))
        self.button_group.add_button(button_group.GroupButton(self.button_group, 1, 0, chr(custom_font.CHAR_ARROW2_N)))
        self.button_group.add_button(button_group.GroupButton(self.button_group, 1, 0, chr(custom_font.CHAR_DARROW_H)))

    def update(self, key, mouse):
        self.button_group.run(key, mouse)
        for button in self.buttons:
            if self.active:
                button.run(key, mouse)


class NewGame(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.log_message('Starting new game')
        self.parent.close()
        self.gEngine.remove_module(self.gEngine.get_module_by_name("MainMenu"))

        self.gEngine.log_close_block()
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

        # Stick player usable modules below to keep them separate from dev mods
        inv_mod = inventory_module.InventoryModule(self.gEngine, g, 0, 0, 35, 40, "Gold: %d" % g.player.fighter.money)
        self.gEngine.add_module(inv_mod)
        inv_mod.deactivate()

        eq_mod = inventory_module.EquipmentModule(self.gEngine, g, 36, 0, 35, 25, "Equipment")
        self.gEngine.add_module(eq_mod)
        eq_mod.deactivate()

        # load this module last
        m = module_list.ModuleList(self.gEngine, g, 0, 0, 15, 5, 'Module List')
        self.gEngine.add_module(m)


class CloseGame(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.log_message('Quitting game')
        self.gEngine.remove_module(self.gEngine.get_module_by_name("MainMenu"))
        self.gEngine.remove_module(self.parent)
        self.gEngine.log_close_block()
        exit(42069)  # more lmao


class LoadGame(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.log_message('loading game')
        self.gEngine.remove_module(self.gEngine.get_module_by_name("MainMenu"))
        self.gEngine.remove_module(self.parent)
        self.gEngine.log_close_block()


class DevMode(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.log_message('Entering Devmode')
        self.gEngine.remove_module(self.gEngine.get_module_by_name("MainMenu"))
        self.gEngine.remove_module(self.parent)
        d = dev_mode.DevMode(self.gEngine)
        self.gEngine.add_module(d)
        self.gEngine.log_close_block()


class Options(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.log_message('Loading options')
        option = options_module.OptionsModule(self.gEngine, None, 0, 0, 25, 7, "Options")
        option.setup()
        self.gEngine.add_module(option)
        self.parent.deactivate()


class Login(button_widget.TextButtonWidget):
    def trigger(self):
        login = login_module.LoginMenu(self.gEngine, None, self.gEngine.SCREEN_WIDTH / 4,
                                       self.gEngine.SCREEN_HEIGHT / 4,
                                       25, 7, "Login")
        login.setup()
        self.gEngine.add_module(login)
        self.parent.deactivate()


class LogoutButton(button_widget.TextButtonWidget):
    def trigger(self):
        self.gEngine.player_id = None


class DiscordButton(button_widget.TextButtonWidget):
    def trigger(self):
        webbrowser.open_new("https://discord.gg/34qASF4")
