from helper_functions import *
from constants import *
from pyglet.math import Vec2
import arcade

class Tile(arcade.Sprite):
    def __init__(self, x, y, state='empty'):
        super().__init__()
        self.x = x
        self.y = y
        self.matrix_to_pixel_position()

        self._state = state  # Only track the state
        self.tower = None

        self.update_texture()

    def __str__(self):
        return f"({self.x}, {self.y}, self.{self._state})"

    def matrix_to_pixel_position(self):
        self.center_x, self.center_y = tile_to_pixel_center(self.x, self.y, TILE_SIZE)

    def set_state(self, state):
        """Set the tile's state. Valid states: 'spawn', 'goal', 'border', 'path', 'empty'."""
        valid_states = {'spawn', 'goal', 'border', 'path', 'empty'}
        if state not in valid_states:
            raise ValueError(f"Invalid state: {state}. Must be one of {valid_states}")
        self._state = state
        self.update_texture()

    def clear_state(self):
        """Clear the tile's state."""
        self.set_state('empty')

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

    def update_texture(self):
        self.texture = TILE_TEXTURES[self._state]

    def link_tower(self, tower):
        self.tower = tower

    def update_position(self, grid_x, grid_y):
        """Update the tile's position."""
        self.x = grid_x
        self.y = grid_y
        self.matrix_to_pixel_position()