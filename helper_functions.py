def get_position_after_move(tile, move):
    """
    Finds the position of the tile after a move

    Args:
        tile (Tile): The tile to find neighbors for
        move (str): The move to find neighbors for

    Returns:
        tuple: A tuple of the new position
    """
    if move == "up":
        return tile.x, tile.y - 1
    elif move == "right":
        return tile.x + 1, tile.y
    elif move == "down":
        return tile.x, tile.y + 1
    elif move == "left":
        return tile.x - 1, tile.y
    else:
        raise ValueError(f"Invalid move: {move}")

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