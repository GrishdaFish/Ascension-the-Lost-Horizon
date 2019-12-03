__author__ = 'GrishdaFish'
import tcod as libtcod


class ThreatEngine:
    def __init__(self, game, gEngine):
        self.game = game
        self.gEngine = gEngine
        self.base_threat = 0
        self.current_threat = 0
        self.threat_thresholds = []

    def calculate_threat(self, scalabliity_factor=1.15, depth=1, depth_factor=10):
        """
        Calculates final threat, called on level change
        :param scalabliity_factor: How much we scale the players threat every level
        :param depth: The depth of the new level being generated
        :param depth_factor: How much to multiply the depth when factoring it into total threat levels
        :return:
        """
        self.current_threat = self.get_player_threat()
        self.current_threat += (depth * depth_factor)
        self.current_threat *= scalabliity_factor
        for threshold in self.threat_thresholds:
            if self.current_threat >= threshold:
                self.base_threat = self.threat_thresholds.pop(threshold)
        print(self.current_threat)

    def get_player_threat(self):
        """
        Calculates player threat based on equipped gear, level, max hit points, accumulated skill points and net worth
        :return:
        """
        player_equipment = self.game.player.fighter.gimmie_da_quips()
        player_inventory = self.game.player.fighter.get_inventory()
        threat = 0
        for object in player_equipment:
            threat += object.item.equipment.threat_level
        for object in player_inventory:
            if object.item.equipment:
                threat += object.item.equipment.threat_level
            if object.item.spell:
                pass
            # todo generate and calculate potion and scrolls threat levels
        threat += (self.game.player.fighter.level * 2)
        threat += (self.game.player.fighter.stat_panel.get_stat_by_name("HP") / 2)
        # todo calculate total spent skill points
        return int(threat)

    def get_current_level_monster_threat(self):
        """
        Returns the threat value of all monsters in a level
        :return:
        """
        threat = 0
        for object in self.game.objects:
            if object.fighter:
                if not self.game.fighter:
                    threat += object.fighter.threat
        return threat

    def get_current_level_item_threat(self):
        """
        Returns the threat level of all items on the ground
        :return:
        """
        threat = 0
        for object in self.game.objects:
            if object.item:
                if object.item.equipment:
                    threat += object.item.equipment.threat_level
                if object.item.spell:
                    pass
        return threat


if __name__ == "__main__":
    class Game:
        def __init__(self):
            self.player = None
            self.objects = []

    class Item:
        def __init__(self, equipment=None):
            self.equipment = equipment
            self.spell = None

    class Equipment:
        def __init__(self):
            self.threat_level = libtcod.random_get_float(0, 0.5, 1.5)

    class Fighter:
        def __init__(self):
            self.level = 1
            self.threat = libtcod.random_get_float(0, 0.5, 1.5)
            self.equipment = []
            self.inventory = []
            self.stat_panel = StatPanel()
            for x in range(10):
                self.equipment.append(Actor(item=Item(Equipment())))
                self.inventory.append(Actor(item=Item(Equipment())))

        def gimmie_da_quips(self):
            return self.equipment

        def get_inventory(self):
            return self.inventory

    class StatPanel:
        def __init__(self):
            self.hp = 15

        def get_stat_by_name(self, x):
            return self.hp

    class Actor:
        def __init__(self, fighter=None, item=None):
            self.item = item
            self.fighter = fighter

    game = Game()
    f = Fighter()
    game.player = Actor(fighter=Fighter())
    for x in range(10):
        game.objects.append(Actor(item=Item(Equipment())))
        game.objects.append(Actor(fighter=Fighter))
    threat_engine = ThreatEngine(game, None)
    threat_engine.calculate_threat()