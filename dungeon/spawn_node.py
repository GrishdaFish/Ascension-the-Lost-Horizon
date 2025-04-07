import tcod as libtcod


class SpawnNode:
    def __init__(self, tile, x, y, game):
        self.tile = tile
        self.x = x
        self.y = y
        self.owner = None
        self.active = True
        self.objects = game.objects
        self.player = game.player
        self.ticker = game.ticker
        self.game = game
        # Speed for spawning, need to play around with values
        self.un_explored_speed = 2000  # 200 turn  spawn
        self.explored_speed = 4000  # 400 turn spawn
        self.group = []
        self.threat = 0
        self.max_group_size = 0

    def turn_on(self):
        self.active = True

    def turn_off(self):
        self.active = False

    def remove_from_group(self, monster):
        for mon in self.group:
            if mon == monster:
                self.group.remove(monster)
                break

    def spawn_mobs(self, game):
        pass
        # # #Need to play around with values, mob spawning is too sparse or too great
        # ##NEED MOAR MANA!
        # if not self.active:
        #     if len(self.group) < 2:
        #         self.turn_on()
        #     else:
        #         #self.ticker.schedule_turn(self.explored_speed, self.owner)
        #         return
        # if libtcod.map_is_in_fov(game.fov, self.x, self.y):
        #     ##if the node is in the view of the player, do nothing
        #     ##but schedule the next spawn turn
        #     # self.ticker.schedule_turn(self.explored_speed, self.owner)
        #     pass
        #
        # else:
        #     # todo: pick leaders and subordinates
        #     self.max_group_size = libtcod.random_get_int(0, 2, 9)
        #     base_group_monster = game.build_objects.get_random_monster_name()
        #     for m in range(self.max_group_size):
        #         mon = game.build_objects.create_monster(game, self.x, self.y, mob_name=base_group_monster)
        #         mon.ai.add_node(self)
        #         self.group.append(mon)
        #         #game.logger.log.info(mon.ai.node)
        #         game.objects.append(mon)
        #
        #     self.turn_off()
        #     # self.ticker.schedule_turn(self.explored_speed, self.owner)
        #     for object in self.group:
        #         object.message = game.message
        #         object.objects = game.objects