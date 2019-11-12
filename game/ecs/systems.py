import esper
from game.ecs.components import *
import tcod as libtcod


class MovementProcessor(esper.Processor):
    def process(self):
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x = 0
            vel.y = 0


class DisplayProcessor(esper.Processor):
    def process(self):
        for ent, (display, pos) in self.world.get_components(Display, Position):
            h, s, v = display.gEngine.console_get_char_background(display.console, pos.x, pos.y)
            col = libtcod.Color(0, 0, 0)
            libtcod.color_set_hsv(col, h, s, v)
            # adjust colors for the light map
            fr, fg, fb = display.color
            br, bg, bb = col
            display.gEngine.console_put_char_ex(display.console, pos.x, pos.y, display.char, int(fr),
                                                int(fg),int(fb), br, bg, bb)


class TickerProcessor(esper.Processor):
    def __init__(self):
        self.ticks = 0

    def process(self):
        for ent, (display, pos) in self.world.get_components(Ticker):
            pass
        self.ticks += 1