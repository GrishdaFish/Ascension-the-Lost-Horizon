

class DijikstraPoint:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class DijikstraMap:
    def __init__(self, gEngine, w, h):
        self.max_value = w * h
        self.map = [[self.max_value for x in range(h)] for y in range(w)]
        self.gEngine = gEngine
        self.w = w
        self.h = h
        self.points = []

    def compute(self, dungeon_map):
        while True:
            changes = False
            for x in range(self.w-2): # exclude the outside cells
                for y in range(self.h-2):
                    if not dungeon_map[x][y].blocked:
                        # check directions for lowest value to find the lowest value neighbor
                        valuex1 = self.map[x+1][y]
                        valuex_1 = self.map[x-1][y]
                        valuey1 = self.map[x][y+1]
                        valuey_1 = self.map[x][y-1]
                        valuexy1 = self.map[x+1][y+1]
                        valuexy_1 = self.map[x-1][y-1]
                        valueyx1 = self.map[x-1][y+1]
                        valueyx_1 = self.map[x+1][y-1]
                        value = min(valuex1, valuex_1, valuey1, valuey_1,
                                    valuexy1, valuexy_1, valueyx1, valueyx_1) # lowest value neighbor
                        dif = self.map[x][y] - value # get the difference between target tile and all neighbors
                        if dif > 1: # if the difference is greater than one, set target tile to 1 greater than neighbors
                            self.map[x][y] = value + 1
                            changes = True
            if changes is False:
                break

    def multiply_map(self, value, dungeon_map):
        for x in range(self.w):
            for y in range(self.h):
                if not dungeon_map[x][y].blocked:
                    self.map[x][y] = int(self.map[x][y] * value)

    def add_point(self, x, y, value):
        self.map[x][y] = value
        self.points.append(DijikstraPoint(x, y, value))

    def clear(self):
        self.map = [[self.max_value for x in range(self.h)] for y in range(self.w)]

    def remove_point(self,x, y):
        for point in self.points:
            if point.x == x and point.y == y:
                self.points.remove(point)
        self.clear()
        for point in self.points:
            self.map[point.x][point.y] = point.value
