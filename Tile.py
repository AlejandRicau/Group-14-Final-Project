class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._state = None  # Only track the state

    def set_state(self, state):
        """Set the tile's state. Valid states: 'spawn', 'goal', 'border', 'path'."""
        valid_states = {'spawn', 'goal', 'border', 'path'}
        if state not in valid_states:
            raise ValueError(f"Invalid state: {state}. Must be one of {valid_states}")
        self._state = state

    def clear_state(self):
        """Clear the tile's state."""
        self._state = None

    def get_state(self):
        """Return the current state of the tile."""
        return self._state

    def shortest_path_to(self, other_tile):
        """
        Returns the shortest number of tiles between self and other_tile,
        including start and goal tiles, assuming orthogonal movement.
        """
        dx = abs(self.x - other_tile.x)
        dy = abs(self.y - other_tile.y)
        return dx + dy + 1  # include start and goal tiles

    @property
    def color(self):
        """Return color based on state."""
        if self._state == 'border':
            return 4
        elif self._state == 'goal':
            return 3
        elif self._state == 'spawn':
            return 2
        elif self._state == 'path':
            return 1
        else:
            return 0
