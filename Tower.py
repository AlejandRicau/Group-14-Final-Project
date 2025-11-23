from constants import *
from helper_functions import *
from Enemy import Enemy
import arcade

class Tower(arcade.Sprite):
    def __init__(self, tile, range_r, freq):
        super().__init__()
        self.tile = tile
        self.level = 1

        self.range_radius = range_r
        self.range_display = None
        self.create_range_display()

        self.frequency = freq
        self.on_target = None

        # Set the tower's position to the tile's center
        self.center_x = tile.center_x
        self.center_y = tile.center_y

    def create_range_display(self):
        """
        Creates a circle sprite to display the tower's range
        """
        # Create a circle sprite
        self.range_display = arcade.SpriteCircle(self.range_radius, arcade.color.GRAY)

        # Set the range display's position to the tower's position
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

        # Make it semi-transparent
        self.range_display.alpha = 100  # 0 = fully invisible, 255 = fully opaque

    def toggle_range_display(self):
        """Hide or show the range display"""
        self.range_display.visible = not self.range_display.visible

    def update(self, *args, **kwargs):
        """
        Updates the tower's position to the tile's center
        """
        # Keep tower centered on its tile
        self.center_x = self.tile.center_x
        self.center_y = self.tile.center_y

        # Update range display
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

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
            if distance_measure(
                    self.center_x,
                    self.center_x,
                    enemy.position[0],
                    enemy.position[1]
            ) <= self.range:
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
        super().__init__(tile, range_r=100, freq=1)
        self.texture = TOWER_TEXTURES['base']
