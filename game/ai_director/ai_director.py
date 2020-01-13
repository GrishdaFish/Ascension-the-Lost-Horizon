__author__ = 'GrishdaFish'
import tcod as libtcod
from game.ai_director import threat_engine as  t_engine
import pathlib
import sys
import os
import time
from gEngine import gEngine as GENGINE


class AiDirector:
    def __init__(self, game, gEngine):
        self.game = game
        self.gEngine = gEngine
        self.threat_engine = t_engine.ThreatEngine(game, gEngine)
        self.speed = 10
        self.ambient_light_level = 0.3
        self.master_scaling = 1.0
        self.monster_scaling = 1.0
        self.item_scaling = 1.0
        self.player_stats = {
            'kills': 0,
            'spells cast': 0,
            'potions quaffed': 0,
            'hit points healed': 0,
            'turns taken': 0,
            'steps moved': 0,
            'items left behind': 0,
            'monsters left behind': 0,
            'items sold': 0,
            'gold spent': 0,
            'gold earned': 0,
            'most damage dealt': 0,
            'most damage received': 0,
            'total damage received': 0,
            'total damage dealt': 0,
            'monsters banished': 0,
            'banished monsters killed': 0,
            'banished monsters deaths': 0,
            'banished monsters left behind': 0,
            'champion kills': 0,
            'champion deaths': 0,
            'champions left behind': 0,
            'average level turns': 0,
            'fastest level': 0,
            'longest level': 0,

        }
        self.care_packages = [
            self.add_potion,
            self.add_scroll,
            self.add_equipment,

        ]
        self.punishments = [

        ]

    def take_turn(self):
        pass

    def new_level(self):
        pass

    def get_equipment(self, x=0, y=0, type=None, name=None, mat=None):
        item = self.game.build_objects.build_equipment(self.game, x, y, type, name, mat)
        threat = self.threat_engine.get_item_threat(item)
        item.item.equipment.threat_level = threat
        return item

    def spawn_loot(self):
        pass

    def spawn_monsters(self):
        pass

    def add_monsters(self):
        pass

    def care_package(self):
        pass

    def punish_player(self):
        pass

    def add_potion(self):
        pass

    def add_scroll(self):
        pass

    def add_equipment(self):
        pass

    def spawn_shop(self):
        pass

    def add_champion(self):
        pass

    def add_player_stat(self, stat, amount, override=False):
        """
        Adds a stat to the tracked stat
        :param stat: String to define the stat increase
        :param amount: int amount to be increased
        :return: Nothing
        """
        if stat in self.player_stats:
            if override:
                self.player_stats[stat] = int(amount)
            else:
                self.player_stats[stat] += int(amount)

    def get_player_stat(self, stat):
        if stat in self.player_stats:
            return self.player_stats[stat]
        else:
            return None

    def dump_data(self):
        path = os.path.abspath('.')
        path = os.path.join(path, 'logs', 'data', 'aid')
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        name = 'stats_'+str(int(time.time())) + '.dat'
        path = os.path.join(path, name)
        with open(path, 'w') as file:
            for item in self.player_stats:
                file.write(item + " " + str(self.player_stats[item]) + "\n")
        self.gEngine.network_send_data('submit_win', self.player_stats)

if __name__ == "__main__":
    ad = AiDirector(None, None)
    print(str(int(time.time())))
    for item in ad.player_stats:
        print(item + " " + str(ad.player_stats[item]))