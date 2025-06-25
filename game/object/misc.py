
from gEngine.utilities.widget import button_widget, window_widget, popups
from game import bark


def dummy_function():
    pass


class Misc:
    def __init__(self, use_function=dummy_function, type=None, game=None, owner=None):
        '''
        This class is used for any kind of miscellaneous interactable objects, such as doors, chests, traps, stairs, etc..
        :param use_function: this is a function pointer that gets called on activate
        :param type: is a string descriptor "door", "chest", etc..
        :param game: the main game instance
        '''
        self.use_function = use_function
        self.type = type
        self.is_open = False
        self.locked = True
        self.lock_difficulty = 0
        self.broken = False
        self.lock_popup = None
        self.open_lock_window = None
        self.pick_lock_button = None
        self.bash_lock_button = None
        self.cancel_button = None
        self.owner = owner
        if self.owner:
            self.base_char = self.owner.char


    def activate(self, args=None):
        if self.use_function:
            self.use_function(args) # function pointer

    def attach_owner(self, owner):
        self.owner = owner
        self.base_char = owner.char

    def set_use_function(self, function):
        self.use_function = function

    def set_lock_difficulty(self, difficulty=0):
        self.lock_difficulty = difficulty

    def setup_popups(self):
        x = self.owner.game.dungeon_width / 4
        y = self.owner.game.dungeon_height / 4
        self.lock_popup = popups.MultiConfirm(self.owner.game.gEngine, self.owner.game, x=x, y=y,
                                             w=20, h=7, title="Locked %s" % self.type)  # ,
        # target_console=self.owner.game.dungeon_console)
        self.lock_popup.deactivate()

    def open(self, target=None):
        # TODO: Add a pop up query to pick or bash the lock
        if not self.is_open:
            if not self.locked:
                self.owner.blocks = not self.owner.blocks
                if self.type == 'door':
                    self.owner.char = 'door_open'
                elif self.type == 'chest':
                    self.owner.char = 'chest_open'
                self.owner.game.gEngine.map_change_tile_blocking(self.owner.x, self.owner.y, False, False)
                self.use_function = self.close
                self.is_open = True
                self.owner.game.message.message("You opened the %s." % self.owner.name, 5)
            else:
                self.owner.game.message.message("%s is locked!" % self.owner.name, 5)
                b = bark.Bark(self.owner.game.gEngine, self.owner.game.dungeon_console, self.owner, 10.0, "Locked!")
                self.owner.game.bark_manager.add_bark(b)
                if self.lock_popup:
                    pop_up_f = [self.pick_lock, self.bash_lock, self.close_popup]
                    pop_up_p = [[target], [target], [target]]
                    pop_up_t = ["Pick", "Bash", "Close"]
                    if self.type:
                        pop_up_m = "Do you want to pick, or bash the %s lock?" % self.type
                    else:
                        pop_up_m = "Do you want to pick, or bash the lock?"
                    self.lock_popup.setup(pop_up_m, pop_up_f, pop_up_p, pop_up_t)
                    self.owner.game.gEngine.add_module(self.lock_popup)
                    self.owner.game.gEngine.bring_module_to_front(self.lock_popup)
                    self.lock_popup.activate()


        else:
            return

    def close(self, args=None):
        if self.is_open:
            self.owner.blocks = not self.owner.blocks
            self.owner.char = self.base_char
            self.owner.game.gEngine.map_change_tile_blocking(self.owner.x, self.owner.y, False, True)
            self.owner.game.message.message("%s is closed." % self.owner.name, 5)
            self.use_function = self.open
            self.is_open = False

        elif self.broken:
            self.owner.game.message.message("%s is broken and can't be closed!" % self.owner.name, 5)

        else:
            self.owner.game.message.message("%s is already closed!" % self.owner.name, 5)

    def unlock(self):
        self.locked = False
        self.open()


    def pick_lock(self, callback):
        self.unlock()
        self.owner.game.message.message("You picked the lock!")
        self.lock_popup.close()

    def bash_lock(self, callback):
        self.unlock()
        self.owner.game.message.message("You bashed the lock!")
        self.lock_popup.close()

    def close_popup(self, callback):
        self.lock_popup.close()

