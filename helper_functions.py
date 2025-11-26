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

    # Highest difficulty (5) is the smallest scale interval
    max_scale = overall_max_scale - (difficulty - 1) * scale_step
    min_scale = max_scale - scale_step

    # Detour chance correlated with midpoint of interval
    midpoint = (min_scale + max_scale) / 2
    detour_chance = (midpoint - overall_min_scale) / (overall_max_scale - overall_min_scale)

    return (min_scale, max_scale), detour_chance

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    """
    Compute the shortest distance from point (px, py) to line segment (x1, y1)-(x2, y2)
    using only plain Python operations.

    Parameters:
        px, py (float): The coordinates of the point
        x1, y1 (float): The coordinates of the start of the segment
        x2, y2 (float): The coordinates of the end of the segment

    Returns:
        float: The shortest distance from the point to the segment
    """
    # Vector from start to end of segment
    vx = x2 - x1
    vy = y2 - y1

    # Vector from start to point
    wx = px - x1
    wy = py - y1

    # Project point onto line, computing t parameter
    len_sq = vx*vx + vy*vy
    if len_sq == 0:
        # Segment is a point
        return ((px - x1)**2 + (py - y1)**2)**0.5

    t = (wx * vx + wy * vy) / len_sq
    t = max(0, min(1, t))  # clamp t to [0,1]

    # Closest point on segment
    closest_x = x1 + t * vx
    closest_y = y1 + t * vy

    # Distance from point to the closest point
    return ((px - closest_x)**2 + (py - closest_y)**2)**0.5
