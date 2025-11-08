class Tile:
    def __init__(self, x, y, color=0):
        self.x = x
        self.y = y
        self.color = color
        self.is_spawn = False
        self.is_goal = False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y