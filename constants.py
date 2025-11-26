import arcade
from PIL import Image, ImageDraw
import random

# Game Constants
TILE_SIZE = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game Economy Constants
STARTING_MONEY = 100
STARTING_LIVES = 20

TOWER_COST = 50
ENEMY_REWARD = 15  # Money gained when killing an enemy
ENEMY_PENALTY = 1  # Lives lost when enemy reaches base

# Colors
COLOR_EMPTY = arcade.color.STORMCLOUD               # Dark void for empty space
COLOR_TUNNEL_FLOOR = arcade.color.GRAY              # Concrete floor for steam tunnels
COLOR_TUNNEL_WALL = arcade.color.DARK_SLATE_GRAY    # Dark walls
COLOR_SPAWN = arcade.color.BLUE
COLOR_GOAL = arcade.color.RED
COLOR_BORDER = arcade.color.DARK_BROWN

# Map each tile state to an RGBA color
TILE_COLORS = {
    "empty": COLOR_EMPTY,
    "spawn": COLOR_SPAWN,
    "goal": COLOR_GOAL,
    "border": COLOR_BORDER,
}

# Pre-generate textures for each tile state using PIL
TILE_TEXTURES = {
    state: arcade.Texture(
        name=f"tile-{state}",
        image=Image.new("RGBA", (TILE_SIZE, TILE_SIZE), color)
    )
    for state, color in TILE_COLORS.items()
}


def generate_tunnel_textures():
    """
    Generates 16 textures by carving paths out of solid walls.
    Bitmask: North=1, East=2, South=4, West=8
    """
    textures = {}
    wall_color = (*COLOR_TUNNEL_WALL[:3], 255)
    floor_color = (*COLOR_TUNNEL_FLOOR[:3], 255)

    # Wall thickness (e.g., 5 pixels for size 20)
    w_th = int(TILE_SIZE * 0.25)

    # Calculate inner coordinates for the "Carve"
    # For TILE_SIZE=20, w_th=5:
    # Wall is indices 0..4. Floor starts at 5.
    # Floor ends at 14. Wall starts at 15.

    start = w_th
    end = TILE_SIZE - w_th - 1  # -1 for inclusive indexing (e.g., index 14)

    for mask in range(16):
        # 1. Start with a SOLID WALL block
        img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), wall_color)
        draw = ImageDraw.Draw(img)

        # 2. Carve the CENTER (Always open for a path tile)
        draw.rectangle([start, start, end, end], fill=floor_color)

        # 3. Carve Directions based on bitmask
        # Note: We intentionally overlap with the center to ensure connection

        # North (Bit 1) - Carve Up
        if mask & 1:
            draw.rectangle([start, 0, end, start], fill=floor_color)

        # East (Bit 2) - Carve Right
        if mask & 2:
            draw.rectangle([end, start, TILE_SIZE - 1, end], fill=floor_color)

        # South (Bit 4) - Carve Down
        if mask & 4:
            draw.rectangle([start, end, end, TILE_SIZE - 1], fill=floor_color)

        # West (Bit 8) - Carve Left
        if mask & 8:
            draw.rectangle([0, start, start, end], fill=floor_color)

        textures[mask] = arcade.Texture(name=f"tunnel-{mask}", image=img)

    return textures


# Generate them once at import time
TUNNEL_TEXTURES = generate_tunnel_textures()

# Tower constants
TOWER_SIZE = (TILE_SIZE-5, TILE_SIZE-5)
RANGE_DISPLAY_OPACITY = 100     # out of 255

# Base tower constants
BASE_TOWER_DAMAGE = 40
BASE_TOWER_FREQUENCY = 1
BASE_TOWER_RANGE_RADIUS = 100

# AOE tower constants
AOE_DAMAGE = 15
AOE_FREQUENCY = .6
AOE_RANGE_RADIUS = 150
AOE_DAMAGE_RADIUS = 15

# Chain tower constants
CHAIN_TOWER_DAMAGE = 25
CHAIN_TOWER_FREQUENCY = .5
CHAIN_TOWER_RANGE_RADIUS = 75
CHAIN_TOWER_CHAIN_LENGTH = 15

# Tower textures
TOWER_TEXTURES = {
    "base": arcade.Texture(
        name="base",
        image=Image.new(
            "RGBA", TOWER_SIZE,
            (*arcade.color.PURPLE[:3], 255))
    ),
    "AOE": arcade.Texture(
        name="AOE",
        image=Image.new(
            "RGBA", TOWER_SIZE,
            (*arcade.color.YELLOW[:3], 255))
    ),
    "chain": arcade.Texture(
        name="chain",
        image=Image.new(
            "RGBA", TOWER_SIZE,
            (*arcade.color.LIGHT_GREEN[:3], 255))
    ),
}

'''Spawn and Goal distance from the edge'''
# This is to ensure that the spawn and goal are not on the edge
# There are some trouble in map generation if they are at the edge or on the corner
SPAWN_GOAL_DISTANCE_FROM_EDGE = 2

'''The region of isolation for new spawn and goal'''
# This is to ensure that the new spawn and goal are not too close to the existing spawn and goal
# This is going to be the side length of a square that's 3x3 centered on the new point
DX_REGION_OF_ISOLATION = 3
