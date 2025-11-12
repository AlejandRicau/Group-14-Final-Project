class Tile:
    def __init__(self, x, y, color=0):
        self.x = x
        self.y = y
        self.color = color
        self.is_spawn = False
        self.is_goal = False
        self.is_border = False

    def set_border(self, color=4):
        """Mark this tile as a border tile with a distinct color."""
        self.is_border = True
        self.color = color

    def clear_border(self):
        """Remove border flag and reset color."""
        self.is_border = False
        if not self.is_spawn and not self.is_goal:
            self.color = 0  # return to empty
