__author__ = 'Grishnak'

from gEngine.utilities.widget import window_widget
from gEngine.utilities.widget import button_widget

from game.user_interface.inventory import *

from game.classes import skills

from game.object import object

def get_centered_text(text, width):
    head = text
    s = len(head)
    pos = width - s/2
    return head, pos

class HotBar:
    def __init__(self, x, y, gEngine, con=0):
        """
        Container class to hold and control all of the hot bar slots.
        :param x: x position of the container bar
        :param y: y position of the container bar
        :param gEngine: the main game engine object (for rendering)
        :return: Nothing
        """
        self.con=con
        self.x = x
        self.y = y
        self.gEngine = gEngine
        self.slots = []
        self.window = gEngine.console_new(32, 5)

    def add_slot(self, slot=None, obj=None):
        """
        Adds a slot to the container class
        :param slot: the slot to be added to the container
        :param obj: the object to attach to a slot
        """
        slot.owner = self
        self.slots.append(slot)

    def update(self, mouse, keyboard, game):
        """
        Handles keyboard and mouse input prior to rendering and calls slot.render()
        If activated, calls attached objects use function
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        self.gEngine.console_clear(self.window)
        col = libtcod.white
        self.gEngine.console_set_default_foreground(self.window, col)
        self.gEngine.console_print_frame(self.window, 0, 0, 32, 5, True)
        for slot in self.slots:
            slot.update(mouse, keyboard, game)
        self.render()

    def remove_slot_object(self, slot=None):
        """
        Removes slot object by slot number
        :param slot: The slot number to remove an object
        :return: Nothing
        """
        pass

    def add_slot_object(self, slot, object):
        """
        Add an object to a slot
        :param slot: The slot number to add object to
        :param object: The object to be added
        :return: Nothing
        """
        self.slots[slot].attach_object(object)

    def render(self):
        """
        Renders the bar and each individual slot
        :return:
        """

        for slot in self.slots:
            self.gEngine.console_blit(slot.window, 0, 0, 3, 3, self.window, slot.position, 1, 1.0, 1.0)
        self.gEngine.console_blit(self.window, 0, 0, 32, 5, self.con, self.x, self.y, 1.0, 1.0)

    def reinit_all(self, con):
        self.con = con
        for slot in self.slots:
            slot.reinit()

class HotBarSlot:
    def __init__(self, con, cx, cy, p, label, gEngine):
        """
        Slot that holds a skill or item that the player can quickly use
        :param con: destination console
        :param cx: x position relative to the main screen
        :param cy: y position relative to the main screen
        :param p: position on the bar its self
        :param label: The hotkey for the hotbar (1, 2, 3, etc..)
        :param gEngine: the game engine object (for rendering)
        :return: Nothing
        """
        self.position = p
        self.con = con
        self.cx = cx
        self.cy = cy
        self.name = 'Empty'
        self.label = label
        self.gEngine = gEngine
        self.window = gEngine.console_new(3, 3)
        self.obj = None
        self.owner = None
        self.game = None
        self.obj_selected = False

    def reinit(self):
        self.window = self.gEngine.console_new(3, 3)

    def attach_object(self, obj):
        """
        Attaches an object (scrolls, potions, skills, weapons, wands, etc...) to this class
        :param obj: Object to attach
        :return: Success? (t/f)
        """
        self.obj = obj
        self.name = obj.name
        self.obj_selected = True

    def remove_object(self):
        """
        Removes the attached object
        :return: Success? (t/f)
        """
        self.obj = None
        self.name = 'Empty'
        self.obj_selected = False

    def use(self, game, key, mouse):
        """
        Uses the object in the current slot, or if the slot is empty, opens a widget to choose what to add to the bar

        Note: change this code to suit item and inventory system per game
        :param game:
        :return:
        """
        if self.game is None:
            self.game = game
        turn = False
        if self.obj:
            if isinstance(self.obj, skills.Skill):
               turn = self.obj.use()
            if isinstance(self.obj, object.Object):
                if self.obj.item.spell:
                    if self.obj.item.qty <= 1:
                        for slot in self.owner.slots:  # make sure any of the other slots that use this item are also removed
                            if slot.obj == self.obj and slot != self:
                                slot.remove_object()
                        self.obj.item.use(game.player.fighter.inventory, game.player, game)
                        turn = True
                        self.remove_object()
                    else:
                        self.obj.item.use(game.player.fighter.inventory, game.player, game)
                        turn = True
                elif self.obj.item.equipment: # change this to equip selected item
                    self.obj.item.equipment.equip(self.game.player, self.game, self.obj.item)
                    turn = True
            if turn:
                game.player_action = 'turn-used'
                return 'turn-used'
        else: # This is the selection mechanic
            c = SelectPopup(self.gEngine, x = mouse.cx, y=mouse.cy-5, w=12,h=4,title="")
            c.setup(self)
            self.gEngine.add_module(c)

    def choose_inventory(self):
        chosen_item = inventory(self.con, self.game.player, self.game)
        if chosen_item:
            self.attach_object(chosen_item)

    def choose_skill(self):
        c = SkillSelectPopup(self.gEngine,x=self.cx, y=self.cy-5, w=20,h=5,title="")
        c.setup(self.game.player, self)
        self.gEngine.add_module(c)

    def update(self, mouse, key, game):
        """
        Handles keyboard and mouse input prior to rendering and calls self.render()
        If activated, calls attached objects use function
        :param game: The main game instance
        :param mouse: mouse input
        :param key: key input
        :return: Activated? (t/f)
        """
        self.gEngine.console_clear(self.window)
        col = libtcod.white

        if self.in_slot(mouse):
            col = libtcod.green
            t = self.name.capitalize()
            t = chr(libtcod.CHAR_TEEW) + t

            # TODO: Refactor this and move it to attach object, add in a UI_NAME type variable for objects
            # TODO: Additionally, add an update_ui_name() function and call to update cooldowns and stuff
            if isinstance(self.obj, skills.Skill):
                if isinstance(self.obj, skills.ResourceSkill):
                    t += ' (Cost: %d %s)' % (self.obj.resource_cost, self.obj.resource_requirement)
                elif isinstance(self.obj, skills.CooldownSkill):
                    t += ' (%d Turn Cooldown)'% self.obj.cooldown
            elif isinstance(self.obj, object.Object):
                if self.obj.item:
                    t += ' (Qty: %d)' % self.obj.item.qty

            t += chr(libtcod.CHAR_TEEE)
            t, p = get_centered_text(t, 16)
            self.gEngine.console_print(self.owner.window, p, 0, t)

            if mouse.lbutton:
                col = libtcod.red
            if mouse.lbutton or key.c == int(self.label):
                self.use(game, key, mouse)
            if mouse.rbutton:
                self.remove_object()
        if key.c:
            if (int(key.c)-48) == int(self.label): # -48 on the key.c to get the offset keyboard character
                self.use(game, key, mouse)

        self.gEngine.console_set_default_foreground(self.window, col)
        self.gEngine.console_print_frame(self.window, 0, 0, 3, 3, True)
        self.gEngine.console_print(self.window, 0, 0, self.label)

        if self.obj:
            c = color_text(self.obj.char, self.obj.color)
            self.gEngine.console_print(self.window, 1, 1, c)
        else:
            c = color_text('X', libtcod.red)
            self.gEngine.console_print(self.window, 1, 1, c)

    def in_slot(self, mouse):
        """
        Checks to see if the mouse is hovering over this hotbar slot
        :param mouse:
        :return:
        """
        if self.cx <= mouse.cx <= self.cx + 2:
            if self.cy <= mouse.cy <= self.cy + 2:
                return True
        return False


class SelectPopup(window_widget.WindowWidget):
    def setup(self, slot):
        self.buttons = []
        self.slot = slot

        self.inventory_button = button_widget.TextButtonWidget(self, 1, 1, "Inventory", slot.choose_inventory)
        self.buttons.append(self.inventory_button)

        self.skill_button = button_widget.TextButtonWidget(self, 1, 2, "Skills", slot.choose_skill)
        self.buttons.append(self.skill_button)

    def update(self, key, mouse):
        if self.slot.obj_selected:
            self.close()
        else:
            for button in self.buttons:
                button.run(key, mouse)

    def close(self):
        self.on_exit()
        self.gEngine.remove_module(self)

class SkillSelectPopup(window_widget.WindowWidget):
    def setup(self, player, slot):
        self.player = player
        self.buttons = []
        self.slot = slot
        y=1
        for skill in self.player.fighter.active_skills:
            b = SkillButton(self, 1, y, label=skill.name, function=None)
            b.setup(skill, self.slot)
            self.buttons.append(b)
            y+=1

    def update(self, key, mouse):
        if self.slot.obj_selected:
            self.close()
        else:
            for button in self.buttons:
                button.run(key, mouse)

    def close(self):
        self.on_exit()
        self.gEngine.remove_module(self)


class SkillButton(button_widget.TextButtonWidget):
    def setup(self, skill, slot):
        self.skill = skill
        self.function = self.fun
        self.slot = slot

    def fun(self):
        self.slot.attach_object(self.skill)
