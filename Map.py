from constants import *
from Tile import Tile
from helper_functions import *

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.generate_new_map()

    def generate_new_map(self):
        """Completely resets the map with new spawn and goal locations."""
        self.map = [[Tile(x, y) for x in range(self.width)] for y in range(self.height)]

        # mark the border
        for row in self.map:
            row[0].color = 1
            row[-1].color = 1
        for tile in self.map[0]:
            tile.color = 1
        for tile in self.map[-1]:
            tile.color = 1

        # mark the spawn and goal
        self.spawn = []
        self.goal = []

        spawn_tile, goal_tile = self.generate_opposite_side_positions(offset=SPAWN_GOAL_DISTANCE_FROM_EDGE)

        spawn_tile.is_spawn = True
        spawn_tile.color = 2
        self.spawn.append(spawn_tile)

        goal_tile.is_goal = True
        goal_tile.color = 3
        self.goal.append(goal_tile)

    def generate_opposite_side_positions(self, offset=3):
        """
        Generates spawn and goal tiles near opposite edges of the map
        but not on the border itself.

        Args:
            offset (int): Minimum distance from the border.

        Returns:
            tuple(Tile, Tile): (spawn_tile, goal_tile)
        """
        # Choose orientation: horizontal or vertical
        orientation = random.choice(["horizontal", "vertical"])

        if orientation == "horizontal":
            # Spawn near left edge, goal near right edge
            spawn_x = random.randint(offset, offset + 2)
            goal_x = random.randint(self.width - 1 - offset - 2, self.width - 1 - offset)
            spawn_y = random.randint(offset, self.height - 1 - offset)
            goal_y = random.randint(offset, self.height - 1 - offset)

        else:
            # Spawn near top edge, goal near bottom edge
            spawn_y = random.randint(offset, offset + 2)
            goal_y = random.randint(self.height - 1 - offset - 2, self.height - 1 - offset)
            spawn_x = random.randint(offset, self.width - 1 - offset)
            goal_x = random.randint(offset, self.width - 1 - offset)

        return self.map[spawn_y][spawn_x], self.map[goal_y][goal_x]

    def get_random_position_on_map(self):
        offset = SPAWN_GOAL_DISTANCE_FROM_EDGE
        random_height = random.randint(offset, self.height - 1 - offset)
        random_width = random.randint(offset, self.width - 1 - offset)
        return self.map[random_height][random_width]

    def recursive_path_generation(self, start_tile, goal_tile=None, detour_chance=0.1):
        """
            Generates a path from start_tile to goal_tile using DFS.
            Returns the path as a list of tiles if successful, else None.

            Args:
                start_tile (Tile): Starting tile
                goal_tile (Tile): Goal tile (default: self.goal[0])
                detour_chance (float): Probability to take random detour

            Returns:
                list[Tile] | None: The path from start to goal
            """
        self.clear_the_map()
        if goal_tile is None:
            goal_tile = self.goal[0]

        visited = set()
        path = {}

        success = self.recursive_path_helper(start_tile, goal_tile, visited, path, detour_chance)
        while not success:
            visited = set()
            path = {}
            success = self.recursive_path_helper(start_tile, goal_tile, visited, path, detour_chance)

        # Color the final path
        for t in path.values():
            t.color = 1
        for spawn in self.spawn:
            spawn.color = 2
        for goal in self.goal:
            goal.color = 3
        return path


    def recursive_path_helper(self, tile, goal_tile, visited, path, detour_chance):
        """
        Recursive DFS helper function.
        """
        # Base cases
        if tile.color == 1:
            return False
        if self.check_2x2_path_cluster(tile, path):
            return False
        if self.check_too_many_adjacent_neighbors(tile, path):
            return False  # <-- NEW check
        if (tile.x, tile.y) in visited:
            return False

        visited.add((tile.x, tile.y))
        path[(tile.x, tile.y)] = tile

        # Goal check
        if tile == goal_tile:
            return True

        # Get directions (goal-directed, optionally detouring)
        directions = self.get_shuffled_directions_toward_goal(tile, detour_chance)
        for direction in directions:
            neighbor = self.get_neighboring_tile(tile, direction)
            if neighbor and self.recursive_path_helper(neighbor, goal_tile, visited, path, detour_chance):
                return True

        # Backtrack
        del path[(tile.x, tile.y)]
        return False

    def get_shuffled_directions_toward_goal(self, tile, detour_chance=0.4):
        """Returns a list of directions toward the goal, shuffled with
        preferred directions first and unpreferred directions after.

        Args:
            tile (Tile): The tile to find neighbors for
            detour_chance (float): Chance of taking a detour

        Returns:
            list: A list of possible moves
        """
        # Get all possible moves
        all_moves = ["up", "right", "down", "left"]

        # Get preferred moves
        dx = self.goal[0].x - tile.x
        dy = self.goal[0].y - tile.y

        # Get preferred moves
        preferred = []
        if dx > 0:
            preferred.append('right')
        elif dx < 0:
            preferred.append('left')

        if dy > 0:
            preferred.append('up')
        elif dy < 0:
            preferred.append('down')

        # Get unpreferred moves
        unpreferred = [d for d in all_moves if d not in preferred]

        # Shuffle preferred and unpreferred moves
        random.shuffle(preferred)
        random.shuffle(unpreferred)

        # Apply detour: sometimes choose a random move instead of preferred
        if random.random() < detour_chance:
            # Randomize all possible moves
            random.shuffle(all_moves)
            return all_moves
        else:
            # Use preferred + unpreferred as before
            return preferred + unpreferred

    def get_neighboring_tile(self, tile, direction):
        """
        Finds the neighboring tile in the given direction.

        Args:
            tile (Tile): The tile to find neighbors for
            direction (str): The direction to find neighbors for

        Returns:
            Tile: The neighboring tile object
        """
        if direction == "up":
            return self.map[tile.y+1][tile.x]
        elif direction == "right":
            return self.map[tile.y][tile.x+1]
        elif direction == "down":
            return self.map[tile.y-1][tile.x]
        else:
            return self.map[tile.y][tile.x-1]

    def path_gen_next_step_finder(self, tile):
        """
        Finds the options for next step at current location.

        Args:
            tile (Tile): The tile to find neighbors for

        Returns:
            list: A list of possible moves
        """
        # find the possible directions
        directions = ["up", "right", "down", "left"]
        is_border, border = self.check_for_border(tile)
        if is_border:
            directions.remove(self.check_for_border(tile)[1])

        # find the possible moves
        possible_moves = []
        for i, each in enumerate(directions):
            neighbor = self.get_neighboring_tile(tile, each)
            if neighbor.color != 0:
                continue
            '''check the neighbors of neighbor to ensure single-unit width'''
            if self.check_surrounding(neighbor, opposite_direction(each)):
                continue
            possible_moves.append(each)

        return possible_moves

    def clear_the_map(self):
        """Clears the map of all paths."""
        for row in self.map:
            for tile in row:
                tile.color = 0
        for spawn in self.spawn:
            spawn.color = 2
        for goal in self.goal:
            goal.color = 3
        # mark the border
        for row in self.map:
            row[0].color = 1
            row[-1].color = 1
        for tile in self.map[0]:
            tile.color = 1
        for tile in self.map[-1]:
            tile.color = 1

    def check_for_border(self, tile):
        """
        Checks if the tile is on the border of the map.

        Args:
            tile (Tile): The tile to check

        Returns:
            tuple: A tuple of (bool, str) where the bool is True if the
            tile is on the border and the str is the direction of the border
        """
        if tile.x == 0:
            return True, 'up'
        elif tile.x == self.width - 1:
            return True, 'down'
        elif tile.y == 0:
            return True, 'left'
        elif tile.y == self.height - 1:
            return True, 'right'

        return False, None

    def check_surrounding(self, tile, from_dir):
        """
        Checks if the tile is surrounded by walls.

        Args:
            tile (Tile): The tile to check
            from_dir (str): The direction from which the tile is being checked

        Returns:
            bool: True if the tile is surrounded by walls, False otherwise
        """
        directions = ["up", "right", "down", "left"]
        directions.remove(from_dir)
        is_border, border = self.check_for_border(tile)
        if is_border:
            directions.remove(border)
        for direction in directions:
            if self.get_neighboring_tile(tile, direction).color != 0:
                return True
        return False

    def check_2x2_path_cluster(self, tile, path):
        """
         Checks if placing a tile here would create a 2x2 or larger cluster.

         Args:
             tile (Tile): Tile to check
             path (dict): Current DFS path {(x,y): Tile}

         Returns:
             bool: True if placing this tile would form a 2x2 cluster
         """
        x, y = tile.x, tile.y
        rows = len(self.map)
        cols = len(self.map[0])

        # Offsets for top-left corner of 2x2 blocks including this tile
        offsets = [(0, 0), (-1, 0), (0, -1), (-1, -1)]

        for dx, dy in offsets:
            count = 0
            for dy2 in [0, 1]:
                for dx2 in [0, 1]:
                    nx, ny = x + dx + dx2, y + dy + dy2

                    # Skip out-of-bounds blocks
                    if not (0 <= nx < cols and 0 <= ny < rows):
                        continue

                    neighbor_tile = self.map[ny][nx]

                    # Count tiles that are either already colored (walls/final path) or in current DFS path
                    if neighbor_tile.color != 0 or (nx, ny) in path:
                        count += 1

            if count >= 3:
                # Placing tile here would form a 2x2 or larger solid cluster
                return True

        return False

    def check_too_many_adjacent_neighbors(self, tile, path):
        """
        Checks if a tile has more than 1 adjacent neighbor (up, down, left, right)
        that is already part of the path.

        Args:
            tile (Tile): The tile to check
            path (dict): Current DFS path

        Returns:
            bool: True if tile has >1 adjacent path neighbors, False otherwise
        """
        x, y = tile.x, tile.y
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # up, right, down, left
        count = 0

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in path:
                count += 1

        return count > 1


