

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Display:
    def __init__(self, c, color, gEngine, console=0):
        self.gEngine = gEngine
        self.char = c
        self.color = color
        self.console = console


class Velocity:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Light:
    def __init__(self, intensity=0.1, variation=0.0):
        self.intensity = intensity
        self.variation = variation


class Ticker:
    def __init__(self, speed=10, player=False):
        self.speed = speed
        self.player = player
        self.next_turn = 0