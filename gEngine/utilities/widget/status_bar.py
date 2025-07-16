__author__ = 'GrishdaFish'
import panels

class StatusBar(panels.StaticPanel):
    def __init__(self, full_color: object, empty_color: object, parent: any, bar_owner: any, x: int=0, y: int=0, w: int=0, h: int=5, title: str="", draw_frame: bool=False)->None:
        """

        :param full_color:
        :param empty_color:
        :param parent:
        :param bar_owner:
        :param gEngine:
        :param x:
        :param y:
        :param w:
        :param h:
        :param title:
        :param draw_frame:
        """
        super().__init__(parent.gEngine, parent, x, y, w, h, title, draw_frame)
        self.bar = self.gEngine.image_new(w * 2, 2)
        self.size = w
        self.full_color = full_color
        self.empty_color = empty_color
        self.parent = parent
        self.bar_owner = bar_owner

    def update(self, key, mouse):
        pass