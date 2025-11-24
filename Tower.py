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

        self.target_dot = None
        self.create_target_dot()

        self.frequency = freq
        self.on_target: Enemy | None = None       #<-- Enemy currently being targeted

        # Set the tower's position to the tile's center
        self.center_x = tile.center_x
        self.center_y = tile.center_y

    def update(self, *args, **kwargs):
        """
        Updates the tower's internal logic
        """
        self.update_position_for_map_expansion()
        self.update_display_texture()
        self.update_target_dot()

    def update_position_for_map_expansion(self):
        """
        Updates the tower's position to the tile's center, made for map expansion
        """
        # Keep tower centered on its tile
        self.center_x = self.tile.center_x
        self.center_y = self.tile.center_y

        # Update range display
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

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
        self.range_display.alpha = 100      #<-- [0, 255]

    def toggle_range_display(self):
        """Hide or show the range display"""
        self.range_display.visible = not self.range_display.visible

    def update_display_texture(self):
        """Updates the range display texture based on the tower's state"""
        # If tower is on target, color red, else gray
        if self.on_target:
            color = arcade.color.RED
        else:
            color = arcade.color.GRAY

        # Replace the texture dynamically
        diameter = self.range_radius * 2
        new_tex = arcade.make_circle_texture(diameter, color)
        self.range_display.texture = new_tex
        self.range_display.alpha = 100

    def create_target_dot(self):
        """Creates a circular target aim as a Sprite"""
        self.target_dot = arcade.SpriteCircle(5, arcade.color.RED)
        self.target_dot.visible = False     # Make it invisible
        self.target_dot.center_x = self.tile.center_x
        self.target_dot.center_y = self.tile.center_y

    def update_target_dot(self):
        """Updates the target dot's position to the tower's tile"""
        if self.on_target:
            self.target_dot.center_x = self.on_target.center_x
            self.target_dot.center_y = self.on_target.center_y
            self.target_dot.visible = True
        else:
            self.target_dot.center_x = self.center_x
            self.target_dot.center_y = self.center_y
            self.target_dot.visible = False

    def upgrade(self):
        self.level += 1



class BaseTower(Tower):
    def __init__(self, tile):
        super().__init__(tile, range_r=100, freq=1)
        self.texture = TOWER_TEXTURES['base']
