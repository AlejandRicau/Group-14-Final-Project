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
        Creates a circular range display as a Sprite with a proper hitbox
        """
        # Create a circle texture
        diameter = self.range_radius * 2
        circle_tex = arcade.make_circle_texture(diameter, arcade.color.GRAY)

        # Create a Sprite with that texture
        self.range_display = arcade.Sprite()
        self.range_display.texture = circle_tex

        # Set position
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

        # Make it semi-transparent
        self.range_display.alpha = 100

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

    def update_display_texture(self, state):
        diameter = self.range_radius * 2
        if state == 'idle':
            color = arcade.color.GRAY
        elif state == 'active':
            color = arcade.color.RED
        else:
            print(f"Invalid state: {state}")
            return

        # Replace the texture dynamically
        new_tex = arcade.make_circle_texture(diameter, color)
        self.range_display.texture = new_tex
        self.range_display.alpha = 100

    def upgrade(self):
        self.level += 1



class BaseTower(Tower):
    def __init__(self, tile):
        super().__init__(tile, range_r=100, freq=1)
        self.texture = TOWER_TEXTURES['base']
