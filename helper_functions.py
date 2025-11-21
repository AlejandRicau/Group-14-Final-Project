import math

def opposite_direction(direction):
    """
    Finds the opposite direction of the given direction

    Args:
        direction (str): The direction to find the opposite for

    Returns:
        str: The opposite direction
    """
    if direction == "up":
        return "down"
    elif direction == "right":
        return "left"
    elif direction == "down":
        return "up"
    else:
        return "right"

def get_path_scale_and_detour(difficulty):
    """
    Returns a linear scale range and detour chance for a given difficulty level.
    Scale ranges are contiguous, non-overlapping, and decrease linearly.

    Parameters:
        difficulty (int): 1 (easiest) to 5 (hardest)

    Returns:
        tuple: (scale_range, detour_chance)
            scale_range: (min_scale, max_scale) for this difficulty
            detour_chance: float between 0-1 correlated with difficulty
    """
    if not (1 <= difficulty <= 5):
        raise ValueError("Difficulty must be between 1 and 5")

    # Overall min/max scale values
    overall_min_scale = 1.0  # shortest path, hardest
    overall_max_scale = 2.0  # longest path, easiest

    total_levels = 5
    scale_step = (overall_max_scale - overall_min_scale) / total_levels

    # Highest difficulty (5) is smallest scale interval
    max_scale = overall_max_scale - (difficulty - 1) * scale_step
    min_scale = max_scale - scale_step

    # Detour chance correlated with midpoint of interval
    midpoint = (min_scale + max_scale) / 2
    detour_chance = (midpoint - overall_min_scale) / (overall_max_scale - overall_min_scale)

    return (min_scale, max_scale), detour_chance

def tile_to_pixel_center(x, y, tile_size):
    """
    Convert tile coordinates (x, y) to pixel coordinates of the tile's center.

    Args:
        x (int): tile x-coordinate
        y (int): tile y-coordinate
        tile_size (int): size of one tile in pixels

    Returns:
        (float, float): pixel coordinates (center_x, center_y)
    """
    center_x = x * tile_size + tile_size / 2
    center_y = y * tile_size + tile_size / 2
    return center_x, center_y

def distance_measure(x1, y1, x2, y2):
    """
    Returns the Euclidean distance between two points.

    Args:
        x1 (float): x-coordinate of the first point
        y1 (float): y-coordinate of the first point
        x2 (float): x-coordinate of the second point
        y2 (float): y-coordinate of the second point

    Returns:
        float: Euclidean distance between the two points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def pixel_to_tile(x, y, tile_size):
    """
    Convert pixel coordinates (x, y) to tile coordinates (tx, ty),
    assuming (0,0) in pixels is the bottom-left of tile (0,0).

    Args:
        x (float): pixel x-coordinate
        y (float): pixel y-coordinate
        tile_size (int): size of one tile in pixels

    Returns:
        (int, int): tile coordinates (tx, ty)
    """
    tx = int(x // tile_size)
    ty = int(y // tile_size)
    return tx, ty

