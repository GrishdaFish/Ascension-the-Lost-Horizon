import tcod as libtcod
import time

class CheckBox:
    # chr(224) = open box, chr(225) = checked box
    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        self.is_checked = False
        self.char = chr(224)  # position of the check box in the GS_TC type font
        self.label = label

    def render(self, target=None, game=None):
        if target and game:
            msg = self.char
            if self.label:
                msg += ' ' + self.label
            game.gEngine.console_print(target, self.x, self.y, msg)
        elif not target and game:
            msg = self.char
            if self.label:
                msg += ' ' + self.label
            game.gEngine.console_print(game.gEngine.root, self.x, self.y, msg)
        elif not target and not game:
            msg = self.char
            if self.label:
                msg += ' ' + self.label
            libtcod.console_print(0, self.x, self.y, msg)

    def update(self, mouse=None, width=None):
        if not width:
            width = 0
        else:
            width = width/2
        if mouse:
            #print(mouse.cx - int(width/2))
            if (mouse.cx - width) == self.x and mouse.cy == self.y:
                if mouse.lbutton:
                    time.sleep(0.1)
                    self.is_checked = not self.is_checked
                    self.change_button()
                    return True
        return False

    def change_button(self):
        if not self.is_checked:
            self.char = chr(224)
        else:
            self.char = chr(225)

    def get_checked(self):
        return self.is_checked

    def set_checked(self, check):
        self.is_checked = check
        self.change_button()
