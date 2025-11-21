import arcade
from PIL import Image
import random

TILE_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
COLOR_EMPTY = arcade.color.LIGHT_GRAY
COLOR_PATH = arcade.color.SEA_GREEN
COLOR_SPAWN = arcade.color.BLUE
COLOR_GOAL = arcade.color.RED
COLOR_BORDER = arcade.color.DARK_BROWN
COLOR_TOWER = arcade.color.YELLOW

# Map each state to an RGBA color
TILE_COLORS = {
    "empty": (*arcade.color.LIGHT_GRAY[:3], 255),
    "path": (*arcade.color.SEA_GREEN[:3], 255),
    "spawn": (*arcade.color.BLUE[:3], 255),
    "goal": (*arcade.color.RED[:3], 255),
    "border": (*arcade.color.DARK_BROWN[:3], 255),
    "tower": (*arcade.color.YELLOW[:3], 255),
}

# Pre-generate textures for each state using PIL
TILE_TEXTURES = {
    state: arcade.Texture(
        name=f"tile-{state}",
        image=Image.new("RGBA", (TILE_SIZE, TILE_SIZE), color)
    )
    for state, color in TILE_COLORS.items()
}

'''Spawn and Goal distance from the edge'''
# This is to ensure that the spawn and goal are not on the edge
# There are some trouble in map generation if they are at the edge or on the corner
SPAWN_GOAL_DISTANCE_FROM_EDGE = 2

'''The region of isolation for new spawn and goal'''
# This is to ensure that the new spawn and goal are not too close to the existing spawn and goal
# This is going to be the side length of a square that's 3x3 centered on the new point
DX_REGION_OF_ISOLATION = 3
