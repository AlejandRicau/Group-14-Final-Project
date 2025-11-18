from constants import *
from Tile import Tile
from helper_functions import *

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.difficulty = 4
        self.generate_new_map()

    def generate_new_map(self):
        """Completely resets the map with new spawn and goal locations."""
        self.map = [[Tile(x, y) for x in range(self.width)] for y in range(self.height)]

        # mark the border
        self.make_border()

        # mark the spawn and goal
        self.spawns = []
        self.goals = []

        spawn_tile, goal_tile = self.generate_opposite_side_positions(offset=SPAWN_GOAL_DISTANCE_FROM_EDGE)

        spawn_tile.set_state('spawn')
        self.spawns.append(spawn_tile)

        goal_tile.set_state('goal')
        self.goals.append(goal_tile)

    def make_border(self):
        """Marks the border tiles with a distinct color."""
        for y in range(self.height):
            for x in range(self.width):
                if y in (0, self.height - 1) or x in (0, self.width - 1):
                    self.map[y][x].set_state('border')

    def generate_opposite_side_positions(self, offset=3):
        """
        Generates spawn and goal tiles near opposite edges of the map,
        with random side assignment (left-right or top-bottom).

        Args:
            offset (int): Minimum distance from the border.

        Returns:
            tuple(Tile, Tile): (spawn_tile, goal_tile)
        """
        # Randomly choose orientation
        orientation = random.choice(["horizontal", "vertical"])

        if orientation == "horizontal":
            # Randomly choose which side the spawn starts on
            spawn_on_left = random.choice([True, False])

            if spawn_on_left:
                spawn_x = random.randint(offset, offset + 2)
                goal_x = random.randint(self.width - 1 - offset - 2, self.width - 1 - offset)
            else:
                spawn_x = random.randint(self.width - 1 - offset - 2, self.width - 1 - offset)
                goal_x = random.randint(offset, offset + 2)

            spawn_y = random.randint(offset, self.height - 1 - offset)
            goal_y = random.randint(offset, self.height - 1 - offset)

        else:  # vertical
            spawn_on_top = random.choice([True, False])

            if spawn_on_top:
                spawn_y = random.randint(offset, offset + 2)
                goal_y = random.randint(self.height - 1 - offset - 2, self.height - 1 - offset)
            else:
                spawn_y = random.randint(self.height - 1 - offset - 2, self.height - 1 - offset)
                goal_y = random.randint(offset, offset + 2)

            spawn_x = random.randint(offset, self.width - 1 - offset)
            goal_x = random.randint(offset, self.width - 1 - offset)

        return self.map[spawn_y][spawn_x], self.map[goal_y][goal_x]

    def expand_map(self, add_width=0, add_height=0, add_new_spawns_goals=False):
        """
        Expands the current map outward by the given width and height increments.
        Keeps existing spawns, goals, and tiles in the center of the new map.
        Optionally adds new spawns and goals.

        Args:
            add_width (int): Number of tiles to add to the width.
            add_height (int): Number of tiles to add to the height.
            add_new_spawns_goals (bool): Whether to add new spawns and goals.
        """
        # --- Compute new dimensions ---
        new_width = self.width + add_width
        new_height = self.height + add_height

        # --- Create new tile grid ---
        new_map = [[Tile(x, y) for x in range(new_width)] for y in range(new_height)]

        # --- Center offset for placing old map inside new one ---
        x_offset = (new_width - self.width) // 2
        y_offset = (new_height - self.height) // 2

        # --- Copy old tiles into new map ---
        for y in range(self.height):
            for x in range(self.width):
                old_tile = self.map[y][x]
                new_tile = new_map[y + y_offset][x + x_offset]

                # Copy properties
                try:
                    new_tile.set_state(old_tile.get_state())
                except ValueError:
                    print(old_tile.get_state(), new_tile.get_state())

        # --- Clear all old borders that are now inside the new map ---
        for row in new_map:
            for tile in row:
                if tile.get_state() == 'border':
                    tile.clear_state()

        # --- Update map references and size ---
        self.map = new_map
        self.width = new_width
        self.height = new_height

        # --- Update spawn/goal coordinates ---
        self.spawns = [self.map[tile.y + y_offset][tile.x + x_offset] for tile in self.spawns]
        self.goals = [self.map[tile.y + y_offset][tile.x + x_offset] for tile in self.goals]

        # --- Rebuild the outer border ---
        self.make_border()

        # --- Optionally add new spawns/goals ---
        if add_new_spawns_goals:
            spawn_tile, goal_tile = self.generate_opposite_side_positions(offset=SPAWN_GOAL_DISTANCE_FROM_EDGE)
            spawn_tile.set_state('spawn')
            spawn_tile.color = 2
            goal_tile.set_state('goal')
            goal_tile.color = 3
            self.spawns.append(spawn_tile)
            self.goals.append(goal_tile)

    def recursive_path_generation(self, start_tile, end_tile, detour_chance=0.1):
        """
            Generates a path from start_tile to goal_tile using DFS.
            Returns the path as a list of tiles if successful, else None.

            Args:
                start_tile (Tile): Starting tile
                end_tile (Tile): Goal tile (default: self.goals[0])
                detour_chance (float): Probability to take random detour

            Returns:
                list[Tile]: The path from start to goal
            """
        '''Initialize the map and variables'''
        self.clear_map()
        visited = set()
        path = {}

        '''Define relative parameters'''
        scales, detour_chance = get_path_scale_and_detour(self.difficulty)
        shortest_path_length = start_tile.shortest_path_to(end_tile)

        '''Generate the first path'''
        success = self.recursive_path_helper(start_tile, end_tile, visited, path, detour_chance)

        '''Generate the path until it satisfy the requirement'''
        while True:
            visited = set()
            path = {}
            success = self.recursive_path_helper(start_tile, end_tile, visited, path, detour_chance)
            # Check if the path is in a desired range
            if success and (scales[1] * shortest_path_length > len(path) > scales[0] * shortest_path_length):
                break

        # Color the final path
        for t in path.values():
            t.set_state('path')
        for spawn in self.spawns:
            spawn.set_state('spawn')
        for goal in self.goals:
            goal.set_state('goal')
        return path

    def recursive_path_helper(self, tile, goal_tile, visited, path, detour_chance):
        """
        Recursive DFS helper function.
        """
        # Base cases
        if tile.get_state() == path:
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
        dx = self.goals[0].x - tile.x
        dy = self.goals[0].y - tile.y

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

    def clear_map(self):
        """Clears the map of all paths."""
        for row in self.map:
            for tile in row:
                if tile.get_state() == 'path':
                    tile.clear_state()

    def check_for_border(self, tile, dist=1):
        """
        Checks if the tile is on the border of the map.

        Args:
            tile (Tile): The tile to check
            dist (int): The distance from the border to check

        Returns:
            bool: True if the tile is x dist within the border, False otherwise
        """
        if tile.y >= self.height - dist:
            return True, 'up'
        elif tile.y <= dist - 1:
            return True, 'down'
        elif tile.x <= dist - 1:
            return True, 'left'
        elif tile.x >= self.width - dist:
            return True, 'right'
        return False, None

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
    
    def check_spawn_or_goal_nearby(self, tile, offset=DX_REGION_OF_ISOLATION):
        """
        Checks if a tile is within the region of isolation of any spawn or goal.

        Args:
            tile (Tile): The tile to check
            offset (int): DX by DX region of isolation

        Returns:
            bool: True if tile is within the region of isolation of any spawn or goal, False otherwise
        """
        x, y = tile.x, tile.y
        for row in self.map[y-offset : y+offset+1]:
            for tile in row[x-offset : x+offset+1]:
                if tile.get_state() in ['spawn', 'goal', 'path']:
                    return True
        return False

    def generate_new_special_point(self, pt_type):
        """
        Generates a new spawn or goal point.

        Args:
            pt_type (str): The type of special point to generate

        Returns:
            None: Modify and append the new tile to the list of spawns or goals
        """
        while True:
            # Randomly generate a new Point
            new_point = random.choice(random.choice(self.map))

            # Keep some tiles from the border
            if self.check_for_border(new_point, dist=SPAWN_GOAL_DISTANCE_FROM_EDGE)[0]:
                continue

            # Check if the new point is within the region of isolation of any spawn or goal
            if self.check_spawn_or_goal_nearby(new_point):
                continue

            # If all checks pass, break the while loop
            break

        # Set the new point to spawn or goal
        if pt_type == "spawn":
            new_point.set_state('spawn')
            self.spawns.append(new_point)
        else:
            new_point.set_state('goal')
            self.goals.append(new_point)

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty



