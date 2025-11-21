from constants import *
from helper_functions import *
from Enemy import Enemy
import arcade

class Tower(arcade.Sprite):
    def __init__(self, tile, range_r, freq):
        super().__init__()
        self.tile = tile
        self.center_x, self.center_y = tile_to_pixel_center(tile.x, tile.y, TILE_SIZE)
        self.level = 1
        self.range = range_r
        self.frequency = freq
        self.on_target = None

    def upgrade(self):
        self.level += 1

    def is_enemy_in_range(self, enemy_list):
        """
        Checks if any enemy is in range of the tower

        Args:
            enemy_list (list<Enemy>): List of enemy objects

        Returns:
            bool: True if any enemy is in range, False otherwise
        """
        for enemy in enemy_list:
            if distance_measure(self.center_px[0], self.center_px[1], enemy.position[0], enemy.position[1]) <= self.range:
                return True
        return False

    def find_target(self, enemy_list):
        """
        Finds the closest enemy to the tower

        Args:
            enemy_list (list<Enemy>): List of enemy objects

        Returns:
            Enemy: The closest enemy to the tower
        """
        # if no enemy is in range, return None
        closest_enemy = None
        if not self.is_enemy_in_range():
            return closest_enemy

        # find the closest enemy
        closest_distance = float('inf')
        for enemy in enemy_list:
            distance = distance_measure(self.center_px[0], self.center_px[1], enemy.position[0], enemy.position[1])
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        return closest_enemy

class BaseTower(Tower):
    def __init__(self, tile):
        super().__init__(tile, range_r=1, freq=1)
        self.texture = TOWER_TEXTURES['base']
