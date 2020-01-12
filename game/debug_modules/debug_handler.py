__author__ = 'GrishdaFish'
import tcod as libtcod

class DebugHandler:
    def __init__(self, gEngine, game):
        self.active = True
        self.game = game
        self.gEngine = gEngine
        self.con = self.gEngine.console_new(self.gEngine.SCREEN_WIDTH, self.gEngine.SCREEN_HEIGHT)
        #self.gEngine.console_set_key_color(self.con, libtcod.black)
        self.test_con = self.gEngine.console_new(5, 5)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def on_exit(self):
        self.deactivate()

    def run(self, key, mouse):

        self.gEngine.console_print_frame(self.test_con, 0, 0, 5, 5, True)
        self.gEngine.console_blit(self.test_con, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0)
        #self.gEngine.console_blit(self.con, 0, 0, 0, 0, 0, 0, 0, 0.50, 0.50)
        #self.gEngine.console_flush()