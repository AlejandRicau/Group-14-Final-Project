import arcade
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

# Spawn and Goal distance from the edge
# This is to ensure that the spawn and goal are not on the edge
# There are some trouble in map generation if they are at the edge or on the corner
SPAWN_GOAL_DISTANCE_FROM_EDGE = 2
