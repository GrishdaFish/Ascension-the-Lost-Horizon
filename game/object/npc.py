from game.object import object




class NPC:
    def __init__(self):
        self.owner = None
        self.function = None
        self.inventory = []
        self.img = None
        self.shop_name = None

    def attach_shop(self, shop_name=None, shop_img=None, shop_contents=None, shop_function=None):
        self.shop_name = shop_name
        self.img = shop_img
        self.inventory = shop_contents
        self.function = shop_function

    def activate(self, player, game):
        self.function(game.dungeon_console, player, game, container=self.inventory, bg=self.img, header=self.shop_name)

