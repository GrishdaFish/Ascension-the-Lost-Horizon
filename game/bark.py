import tcod as libtcod
import time

player_found_barks = [
    "Filthy human!",
    "Fresh meat!",
    "Get him!",

]

player_new_level_barks = [
    "I've got a bad feeling about this one",
    "It smells of death in here",
    "Something feels off in here",
    "No good can come of this adventure",
    "What treasures are to be found?"
]

hit_barks = [
    "Ugh!",
    "Ahh!",
    "Oof",
    "Help!",
]


class BarkManager:
    def __init__(self):
        self.barks = []

    def add_bark(self, bark):
        self.barks.append(bark)

    def render_barks(self):
        for bark in self.barks:
            bark.draw()

    def update_barks(self):
        if len(self.barks) == 1:
            if self.barks[0].dead:
                self.barks.pop(0)
        else:
            for bark in range(len(self.barks) - 1, 0, -1):
                if self.barks[bark].dead:
                    self.barks.pop(bark)

        for bark in self.barks:
            if not bark.dead:
                bark.update()

    def remove_bark(self, bark):
        for obark in self.barks:
            if obark == bark:
                self.barks.remove(obark)

    def empty(self, gEngine):
        for x in range(len(self.barks) - 1, 0, -1):
            gEngine.console_remove_console(self.barks[x].console)
        self.barks = []


class Bark:
    def __init__(self, gEngine, console, owner, duration, message):
        self.dead = False
        self.gEngine = gEngine
        self.owner = owner
        self.duration = duration
        self.message = message
        self.width = len(message)
        self.height = 1
        self.console = gEngine.console_new(self.width, self.height)
        self.target_console = console
        self.time_now = time.time()
        self.start_time = time.time()
        self.end_duration = self.time_now + duration
        self.alpha = 1.0

    def draw(self):
        if not self.dead:
            y_pos = self.owner.y - 1
            x_pos = int(self.owner.x - (self.width /2))
            # Clamp bark to the window
            if x_pos < 0:
                x_pos = 0
            elif x_pos + self.width > self.gEngine.w:
                x_pos = self.gEngine.w - self.width
            if y_pos < 0:
                y_pos = self.owner + 1
            self.gEngine.console_blit(self.console, 0, 0, self.width, self.height, self.target_console, x_pos,
                                      y_pos, self.alpha, self.alpha)

    def update(self):
        if not self.dead:
            self.gEngine.console_clear(self.console)
            self.time_now += (time.time() - self.time_now)
        if self.time_now > self.end_duration:
            self.dead = True
            #self.gEngine.console_remove_console(self.console)
        else:
            self.alpha = 1.0 - (time.time() - self.start_time) / self.duration
            self.gEngine.console_print(self.console, 0, 0, self.message)
