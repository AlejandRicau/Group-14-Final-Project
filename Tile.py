from helper_functions import *
from constants import *
import arcade

class Tile(arcade.Sprite):
    def __init__(self, x, y, state='empty'):
        super().__init__()
        self.x = x
        self.y = y
        self.grid_pos = self.x, self.y
        self.matrix_to_pixel_position()

        self._state = state  # Only track the state
        self.tower = None
        self.bitmask = 0

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
        # 1. If it's a tunnel/path, use the bitmask texture
        if self._state == 'path':
            # Default to 0 (all walls) if mask isn't set yet
            self.texture = TUNNEL_TEXTURES.get(self.bitmask, TUNNEL_TEXTURES[0])
            self.scale = 1.0  # Since we generated at TILE_SIZE, scale is 1

        # 2. For Spawn/Goal, you might want to overlay the color ON TOP of the tunnel
        # For now, let's just keep them simple to verify the code works
        elif self._state in TILE_TEXTURES:
            self.texture = TILE_TEXTURES[self._state]
            if self.texture:
                # Recalculate scale for the standard textures
                self.scale = TILE_SIZE / max(self.texture.width, self.texture.height)

    def link_tower(self, tower):
        self.tower = tower

    def update_position(self, grid_x, grid_y):
        """Update the tile's position."""
        self.x = grid_x
        self.y = grid_y
        self.matrix_to_pixel_position()

    def set_bitmask(self, mask):
        self.bitmask = mask
        self.update_texture()

    def get_bitmask(self):
        return self.bitmask

    def is_adjacent_to_path(self, tilemap):
        """
        Check if the tile is adjacent to a path tile.

        Args:
            tilemap (Map): The tilemap to check against.

        Returns:
            bool: True if the tile is adjacent to a path tile, False otherwise.
        """
        for t in tilemap.get_surrounding_tiles(self):
            if t.get_state() == 'path':
                return True
        return False

    def is_valid_tower_location(self, tilemap):
        """
        Check if the tile is a valid location for a tower.

        Args:
            tilemap (Map): The tilemap to check against.

        Returns:
            bool: True if the tile is a valid location for a tower, False otherwise.
        """
        # tile must be empty
        if self.get_state() != 'empty':
            return False

        # tile must touch a path
        return self.is_adjacent_to_path(tilemap)