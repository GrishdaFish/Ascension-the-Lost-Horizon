__author__ = 'GrishdaFish'


class Rect:
    """
    A rectangle shape to hold a room for dungeon generation
    """
    def __init__(self, x=0, y=0, w=0, h=0, doors=None, p=None):
        """
        :param x: x map position
        :param y: y map position
        :param w: width of the room
        :param h: height of the room
        :param doors: a list that holds all of the doors attached to this room, list is a touple with (x, y) positions
        :param p: a 2d list of chars that holds room data
        """
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h
        self.doors = doors
        self.prefab_layout = p

    def center(self):
        """

        :return: returns the center point of the room in (x, y) format
        """
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (int(center_x), int(center_y))

    def intersect(self, other):
        """
        Checks for intersections between 2 Rect() classes
        :param other: another Rect() class to check to see if this one and the other one intersects
        :return: T/F
        """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def outside_border(self):
        return self.x1, self.x2, self.y1, self.y2

