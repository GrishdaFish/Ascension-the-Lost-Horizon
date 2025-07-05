__author__ = 'GrishdaFish'



class StaticPanel:
    def __init__(self, gEngine, parent, x=0, y=0, w=0, h=5, title="", draw_frame=True):
        """
        A static panel used to display information on WindowWidgets. Useful to divide up sections of a Window
        :param gEngine: the active gEngine instance
        :param parent: the parent WindowWidget this is attached to
        :param x: X position in relation to the parent
        :param y: Y position in relation to the parent
        :param w: Width of this panel
        :param h: Height 0f this panel
        :param title: The title to be displayed at the top of this panel, only drawn if the frame is drawn
        :param draw_frame: Whether or not to draw a frame around this panel
        """
        self.gEngine = gEngine
        self.parent = parent
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.title = title
        self.title_position = self.w / 2 - (len(self.title) / 2)
        self.draw_frame = draw_frame
        self.con = self.gEngine.console_new(self.w, self.h)

        # work around until I update other widgets
        self.collapsed = False
        self.minimized = False

    def on_exit(self):
        """
        cleanup for this panel
        :return:
        """
        self.close()
        if self.con:
            self.con = self.gEngine.console_remove_console(self.con)

    def run(self, key, mouse):
        """
        internal logic for the panel. Do not override this, use update() instead
        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return:
        """
        if self.parent.is_active():
            self.gEngine.console_clear(self.con)

            self.pre_draw_widget()
            self.update(key, mouse)

            self.gEngine.console_blit(self.con, 0, 0, 0, 0, self.parent.con, self.x, self.y, 1.0, 1.0)

    def update(self, key, mouse):
        """
        Use this function to provide custom logic and drawing

        :param key: libtcod.Key() object
        :param mouse: libtcod.Mouse() object
        :return:
        """
        pass

    def close(self):
        """
        Override for custom cleanup logic
        :return:
        """
        pass

    def pre_draw_widget(self):
        """
        Used to draw anything that is required to be drawn before custom update() drawing
        :return:
        """
        if self.draw_frame:
            self.gEngine.console_print_frame(self.con, 0, 0, self.w, self.h, True)
            self.gEngine.console_print(self.con, self.title_position, 0, self.title)
