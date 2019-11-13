from game import lights
class Ticker:
    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do
        # {ticks: [obj1, obj2, ...], ticks+1: [...], ...}

    def clear_ticker(self):
        self.ticks = 0
        self.schedule = {}

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def next_turn(self, game):
        things_to_do = self.schedule.pop(self.ticks, [])
        ##SORT THE LIST TO HAVE THE PLAYER TAKE HIS TURN FIRST
        ##Need to check for lists in thing_to_do
        ##if they are lists pop objects from them
        ##until we find the player, then pop the player
        ##and append the rest of the monsters back to the schedule
        ##and then schedule a new turn for the player
        player = False
        for obj in things_to_do:
            if isinstance(obj, lights.LightHandler):
                obj.update()
                obj.add_turn(self)
            elif obj != game.player:
                if obj.ai:
                    ##Simulate monsters until the players turn
                    obj.ai.take_turn(game)
                else:
                    obj.use(game)
                pass

            else:
                ##when its the players turn, confirm,
                ##then apply the rest of the monsters
                player = True
        ##at the moment, monsters get priority for taking turns over the player.
        ##need to tweak this a bit more to get the turn
        return player

    def remove_object(self ,object):
        ##Remove monsters that get killed before they get a turn
        for val in self.schedule.values():
            for obj in val:
                if obj == object:
                    val.remove(object)
                    break

    def get_next_tick(self):
        ##For getting the next tick with a turn, to skip past empty ticks
        ticks = list(self.schedule.keys())
        next_tick = ticks[0]
        for tick in ticks:
            if tick < next_tick:
                next_tick = tick
        self.ticks = next_tick