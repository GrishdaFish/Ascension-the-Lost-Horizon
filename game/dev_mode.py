__author__ = 'Grishnak'
import tcod as libtcod
from dungeon import dungeon
from dungeon import prefab_dungeon
from gEngine.utilities.dijikstra_map import *
from copy import deepcopy
import math
from game.debug_modules import module_list

from game.object import build_objects
from gEngine.utilities.user_interface import hot_bar
from gEngine.utilities.widget import window_widget, text_input_widget, button_group, button_widget, popups


class DevMode:
    def __init__(self, gEngine):
        gEngine.log_open_block("Loading Dev Mode...")
        self.first=True
        self.gEngine = gEngine
        self.active = True
        self.con_w = self.gEngine.w
        self.con_h = 48
        self.con = self.gEngine.console_new(self.con_w, self.con_h)
        self.gEngine.log_message("Dev Mode Console " + str(self.con))

        # Ui variables
        self.screen_width = self.gEngine.w
        self.screen_height = self.gEngine.h
        self.panel_height = 7
        self.dungeon_height = self.screen_height - self.panel_height - 5
        self.dungeon_width = self.screen_width
        self.bar_width = 20
        self.panel_y = self.screen_height - self.panel_height
        self.message_x = self.bar_width + 2
        self.message_width = self.screen_width
        self.message_height = self.panel_height - 1

        # create all of the consoles for drawing and UI
        self.dungeon_console = self.gEngine.console_new(self.dungeon_width, self.dungeon_height)  # main viewport
        self.panel = self.gEngine.console_new(self.screen_width, self.panel_height)  # for messages and others
        self.toolbar = self.gEngine.console_new(self.screen_width, 5)  # for the hotbar
        '''self.gEngine.log_open_block("Initializing Hotbar")
        x = 32 / 2
        x = self.gEngine.w / 2 - x
        self.hotbar = hot_bar.HotBar(x, 0, self.gEngine, self.toolbar)
        z = 1
        index = ord('1')
        for i in range(10):
            if index == ord(':'):
                index = ord('0')
            s = hot_bar.HotBarSlot(None, z + x, self.panel_y - 4, z, chr(index), self.gEngine)
            self.hotbar.add_slot(s)
            z += 3
            index += 1
        self.gEngine.log_message("Hotbar initialized")
        self.gEngine.log_close_block()'''

        self.gEngine.log_open_block("Loading all content")

        self.gEngine.log_message("Loading monsters and items")
        self.content = build_objects.GameObjects(self.gEngine)

        self.gEngine.log_message("Loading Rooms")
        self.prefab_generator = prefab_dungeon.PrefabGenerator(self.dungeon_width, self.dungeon_height, self.gEngine)

        self.gEngine.log_message("Content loaded")
        self.gEngine.log_close_block()

        self.gEngine.log_message("...Dev mode successfully set up!")
        self.gEngine.log_close_block()

        # m = module_list.ModuleList(self.gEngine, None, 0, 0, 15, 5, 'Module List')
        # self.gEngine.add_module(m)
        # self.gEngine.bring_module_to_front(m)

        self.dev_mode_menu = DevModeMenu(self.gEngine, x=0, y=self.panel_y, w=self.screen_width, h=self.panel_height)
        self.dev_mode_menu.setup(self)
        self.dev_mode_menu.activate()
        self.gEngine.add_module(self.dev_mode_menu)

        self.gEngine.log_open_block("Setting up Dev Mode Editors...")
        self.monster_editor = MonsterEditor(self.gEngine, x=0, y=0, w=self.con_w, h=self.con_h, title="Monster Editor")
        self.monster_editor.setup(self.content.monsters)
        self.monster_editor.deactivate()
        self.gEngine.add_module(self.monster_editor)

        self.item_editor = ItemEditor(self.gEngine, x=0, y=0, w=self.con_w, h=self.con_h, title="Item Editor")
        self.item_editor.setup()
        self.item_editor.deactivate()
        self.gEngine.add_module(self.item_editor)

        self.room_editor = RoomEditor(self.gEngine, x=0, y=0, w=self.con_w, h=self.con_h, title="Room Editor")
        self.room_editor.setup()
        self.room_editor.deactivate()
        self.gEngine.add_module(self.room_editor)

        self.gEngine.log_message("Editors set up")
        self.gEngine.log_close_block()



    def run(self, key, mouse):
        if self.first:
            self.gEngine.console_clear(0)
            self.gEngine.log_open_block("Dev mode Running...")
            self.gEngine.log_message(" ")
            self.first = False


        self.render(key, mouse)


    def render(self, key, mouse):
        self.gEngine.console_clear(self.con)
        # self.hotbar.update(mouse, key, self)
        # self.gEngine.console_print(self.con, 1, 1, "(%dfps) Depth: %d" % (self.gEngine.sys_get_fps(), 1))
        # self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
        # self.hotbar.render()
        # self.gEngine.console_blit(self.toolbar, 0, 0, self.gEngine.w, 5, 0, 0, self.panel_y - 5, 1.0, 1.0)

        #self.gEngine.console_flush()


class DevModeMenu(window_widget.WindowWidget):
    def update(self, key, mouse):
        for button in self.buttons:
            if self.active:
                button.run(key, mouse)

    def close(self):
        pass

    def setup(self, dev_mode):
        self.dev_mode = dev_mode
        self.buttons = []
        self.m = MonsterEditorButton(self, 1, 1, "Monster Editor", None, self.dev_mode)
        self.i = ItemEditorButton(self, 1, 2, "Item Editor", None, self.dev_mode)
        self.r = RoomEditorButton(self, 1, 3, "Room Editor", None, self.dev_mode)
        self.buttons.append(self.m)
        self.buttons.append(self.i)
        self.buttons.append(self.r)


class MonsterEditor(window_widget.WindowWidget):
    def update(self, key, mouse):
        if not self.collapsed and not self.minimized:
            self.gEngine.console_print_frame(self.preview_console, 0, 0, 10, 10, True, "Preview ")
            r, g, b = 0, 0, 0
            if len(self.m_color_r.text_field) > 0:
                r = int(self.m_color_r.text_field)
                if r == 0:
                    r = 1
                elif r >= 255:
                    r = 255
            if len(self.m_color_g.text_field) > 0:
                g = int(self.m_color_g.text_field)
                if g == 0:
                    g = 1
                elif g >= 255:
                    g = 255
            if len(self.m_color_b.text_field) > 0:
                b = int(self.m_color_b.text_field)
                if b == 0:
                    b = 1
                elif b >= 255:
                    b = 255
            color = (r, g, b)
            cell = self.gEngine.color_text(self.m_cell.text_field, color)
            self.gEngine.console_print(self.preview_console, 4, 4, cell)
            self.gEngine.console_blit(self.preview_console, 0, 0, 10, 10, self.con, 14, 24, 1.0, 1.0)

            self.gEngine.console_vline(self.con, self.max_width + 2, 1, self.height-2)
            for button in self.monster_edit_buttons:
                button.run(key, mouse)
            self.gEngine.console_print(self.con, 1, 9, "Can Equip Items: ")
            self.m_equip_group.run(key, mouse)
            self.gEngine.console_print(self.con, 1, 11, "Monster size (below)")
            self.m_size_group.run(key, mouse)

            for button in self.ui_buttons:
                button.run(key, mouse)

    def close(self):
        pass

    def setup(self, monsters):
        self.preview_console = self.gEngine.console_new(10, 10)
        self.monsters = monsters
        self.monster_edit_buttons = []
        self.monster_list = []
        self.ui_buttons = []
        self.base_width = 25
        self.max_width = 38
        max_width = self.max_width

        for monster in self.monsters:
            # put together a list of monsters
            self.monster_list.append(monster)

        # Set up the window layout with no monster loaded
        self.m_name = text_input_widget.TextInputWidget(self, "Name: ", 1, 1, max_width)
        self.monster_edit_buttons.append(self.m_name)

        self.m_cell = text_input_widget.TextInputWidget(self, "Cell: ", 1, 2, max_width)
        self.monster_edit_buttons.append(self.m_cell)

        self.m_hp = text_input_widget.TextInputWidget(self, "Hit Points: ", 1, 3, max_width)
        self.monster_edit_buttons.append(self.m_hp)

        self.m_speed = text_input_widget.TextInputWidget(self, "Speed: ", 1, 4, max_width)
        self.monster_edit_buttons.append(self.m_speed)

        self.m_strength = text_input_widget.TextInputWidget(self, "Strength: ", 1, 5, max_width)
        self.monster_edit_buttons.append(self.m_strength)

        self.m_dexterity = text_input_widget.TextInputWidget(self, "Dexterity: ", 1, 6, max_width)
        self.monster_edit_buttons.append(self.m_dexterity)

        self.m_intelligence = text_input_widget.TextInputWidget(self, "Intelligence: ", 1, 7, max_width)
        self.monster_edit_buttons.append(self.m_intelligence)

        self.m_xp = text_input_widget.TextInputWidget(self, "XP Value: ", 1, 8, max_width)
        self.monster_edit_buttons.append(self.m_xp)

        self.m_equip_group = button_group.ButtonGroupWidget(self, 18, 9, 4, 1)
        self.m_equip_group.add_button(button_group.GroupButton(self.m_equip_group, 1, 0, "True"))

        self.m_color_r = text_input_widget.TextInputWidget(self, "Color R: ", 1, 10, 12)
        self.monster_edit_buttons.append(self.m_color_r)
        self.m_color_g = text_input_widget.TextInputWidget(self, "G: ", 14, 10, 6)
        self.monster_edit_buttons.append(self.m_color_g)
        self.m_color_b = text_input_widget.TextInputWidget(self, "B: ", 21, 10, 6)
        self.monster_edit_buttons.append(self.m_color_b)

        # Tiny, Small, Normal, Large, Huge
        self.m_size_group = button_group.ButtonGroupWidget(self, 1, 12, max_width)
        self.m_size_group.add_button(button_group.GroupButton(self.m_size_group, 1, 0, "Tiny"))
        self.m_size_group.add_button(button_group.GroupButton(self.m_size_group, 1, 0, "Small"))
        self.m_size_group.add_button(button_group.GroupButton(self.m_size_group, 1, 0, "Normal"))
        self.m_size_group.add_button(button_group.GroupButton(self.m_size_group, 1, 0, "Large"))
        self.m_size_group.add_button(button_group.GroupButton(self.m_size_group, 1, 0, "Huge"))


        #t = self.gEngine.color_text("New", )
        self.new_button = button_widget.TextButtonWidget(self,2, self.height-2, "New", self.new)
        self.save_button = button_widget.TextButtonWidget(self, 8, self.height - 2, "Save", self.save)
        self.load_button = button_widget.TextButtonWidget(self, 16, self.height-2, "Load", self.load)
        self.clear_button = button_widget.TextButtonWidget(self, 24, self.height-2, "Clear", self.clear)

        self.ui_buttons.append(self.new_button)
        self.ui_buttons.append(self.save_button)
        self.ui_buttons.append(self.load_button)
        # self.ui_buttons.append(self.clear_button)

    def save(self):
        pass

    def new(self):
        for button in self.monster_edit_buttons:
            button.text_field = ""

        self.m_equip_group.disable_all()
        self.m_size_group.disable_all()


    def load(self):
        pass

    def clear(self):
        pass

class ItemEditor(window_widget.WindowWidget):
    def update(self, key, mouse):
        pass

    def close(self):
        pass

    def setup(self):
        pass


class RoomEditor(window_widget.WindowWidget):
    def update(self, key, mouse):
        pass

    def close(self):
        pass

    def setup(self):
        pass


class MonsterEditorButton(button_widget.TextButtonWidget):
    def trigger(self):
        for b in self.passable.dev_mode_menu.buttons:
            b.triggered = False
        self.triggered = True
        self.passable.monster_editor.activate()
        self.passable.item_editor.deactivate()
        self.passable.room_editor.deactivate()
        # self.passable.gEngine.bring_module_to_front(self.passable.monster_editor)


class ItemEditorButton(button_widget.TextButtonWidget):
    def trigger(self):
        for b in self.passable.dev_mode_menu.buttons:
            b.triggered = False
        self.triggered = True
        self.passable.monster_editor.deactivate()
        self.passable.item_editor.activate()
        self.passable.room_editor.deactivate()


class RoomEditorButton(button_widget.TextButtonWidget):
    def trigger(self):
        for b in self.passable.dev_mode_menu.buttons:
            b.triggered = False
        self.triggered = True
        self.passable.monster_editor.deactivate()
        self.passable.item_editor.deactivate()
        self.passable.room_editor.activate()


def setup_monster_text_field(monster):
    pass