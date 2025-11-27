from constants import *
from helper_functions import *
from Tile import Tile
import random

class Map:
    def __init__(self, width, height, difficulty=4):
        """
        Initializes the map with the given width and height.

        Args:
            width (int): The width of the map.
            height (int): The height of the map.
            difficulty (int): The difficulty of the map.
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.map = None
        self.spawns = []
        self.goals = []
        self.generate_new_map()

    def generate_new_map(self):
        """Completely resets the map with new spawn and goal locations."""
        self.map = [[Tile(x, y) for x in range(self.width)] for y in range(self.height)]

        # mark the border
        self.make_border()

        # mark the spawn and goal
        self.spawns = []
        self.goals = []

        '''Generate spawn and goal tiles'''
        spawn_tile, goal_tile = self.generate_opposite_side_positions(
            offset=SPAWN_GOAL_DISTANCE_FROM_EDGE
        )

        spawn_tile.set_state('spawn')
        self.spawns.append(spawn_tile)

        goal_tile.set_state('goal')
        self.goals.append(goal_tile)

    def make_border(self):
        """Marks the border tiles with a distinct color."""
        # Top and bottom row
        for x in range(self.width):
            self.map[0][x].set_state('border')
            self.map[self.height - 1][x].set_state('border')

        # Left and right column (excluding corners already set)
        for y in range(1, self.height - 1):
            self.map[y][0].set_state('border')
            self.map[y][self.width - 1].set_state('border')

    def generate_opposite_side_positions(self, offset=3, offset_range=2):
        """
        Generates spawn and goal tiles in diagonally opposite corners.
        (e.g., Top-Left Spawn -> Bottom-Right Goal)

        Args:
            offset (int): Minimum distance from the border.
            offset_range (int): Range of variation from offset.

        Returns:
            tuple(Tile, Tile): (spawn_tile, goal_tile)
        """
        # 1. Randomly decide which corner the spawn starts in
        # True = Low coordinate (Left or Top), False = High coordinate (Right or Bottom)
        spawn_on_left = random.choice([True, False])
        spawn_on_top = random.choice([True, False])

        # 2. Define Helper to get a random coordinate based on the side (Low or High)
        def get_coordinate(is_low_side, limit):
            if is_low_side:
                # "Low" side (Left or Top)
                return random.randint(offset, offset + offset_range)
            else:
                # "High" side (Right or Bottom)
                return random.randint(limit - 1 - offset - offset_range, limit - 1 - offset)

        # 3. Calculate Spawn Coordinates
        spawn_x = get_coordinate(spawn_on_left, self.width)
        spawn_y = get_coordinate(spawn_on_top, self.height)

        # 4. Calculate Goal Coordinates (MUST be opposite of Spawn)
        # We pass "not spawn_on_left" to force the opposite side
        goal_x = get_coordinate(not spawn_on_left, self.width)
        goal_y = get_coordinate(not spawn_on_top, self.height)

        return self.map[spawn_y][spawn_x], self.map[goal_y][goal_x]

    def expand_map(self, add_width=0, add_height=0):
        """
        Expands the current map outward by the given width and height increments.
        Keeps existing spawns, goals, and tiles in the center of the new map.
        Optionally adds new spawns and goals.

        Args:
            add_width (int): Number of tiles to add to the width.
            add_height (int): Number of tiles to add to the height.
            add_new_spawns_goals (bool): Whether to add new spawns and goals.
        """
        # Compute new dimensions
        new_width = self.width + add_width
        new_height = self.height + add_height

        # Create empty new map matrix
        new_map = [[Tile(x, y) for x in range(new_width)] for y in range(new_height)]

        # Center offset for placing old map inside new one
        x_offset = (new_width - self.width) // 2
        y_offset = (new_height - self.height) // 2

        # Copy old tiles into new map
        for y in range(new_height):
            for x in range(new_width):
                old_x = x - x_offset
                old_y = y - y_offset

                if 0 <= old_x < self.width and 0 <= old_y < self.height:    #
                    new_tile = self.map[old_y][old_x]
                    new_tile.update_position(x, y)  # updates the tile object's internal x,y

                else:
                    new_tile = Tile(x, y)

                new_map[y][x] = new_tile

        # Clear all old borders that are now inside the new map
        for row in new_map:
            for tile in row:
                if tile.get_state() == 'border':
                    tile.clear_state()

        # --- Update map references and size ---
        self.map = new_map
        self.width = new_width
        self.height = new_height

        # --- Update spawn/goal coordinates ---
        self.spawns = [self.map[t.y][t.x] for t in self.spawns]
        self.goals = [self.map[t.y][t.x] for t in self.goals]

        # --- Rebuild the outer border ---
        self.make_border()

    def recursive_path_generation(self, start_tile, end_tile):
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

        # Note the new argument: parent_tile=None

    def recursive_path_helper(self, start_tile, goal_tile, visited, path, detour_chance, depth=0, parent_tile=None):
        """
        Iterative DFS (Depth First Search).
        Uses a stack to simulate recursion, avoiding RecursionError on large maps.
        """
        # Get initial directions for the start tile
        initial_dirs = self.get_shuffled_directions_toward_goal(start_tile, goal_tile, detour_chance)

        # Stack stores context: [current_tile, parent_tile, directions_list]
        stack = [[start_tile, parent_tile, initial_dirs]]

        # Mark start as visited immediately
        visited.add((start_tile.x, start_tile.y))
        path[(start_tile.x, start_tile.y)] = start_tile

        while stack:
            # Peek at the current context (Do not pop yet, we need to know if we must backtrack)
            current_context = stack[-1]
            tile, parent, directions = current_context

            # 1. Check if we found the goal
            if tile == goal_tile:
                return True

            # 2. Try to find a valid move from the remaining directions
            found_valid_move = False

            while directions:
                direction = directions.pop(0)  # Get the next direction
                neighbor = self.get_neighboring_tile(tile, direction)

                if not neighbor:
                    continue

                # Check if this neighbor is valid
                if self._check_tile_validity(neighbor, tile, goal_tile, visited, path):
                    # Valid move found!

                    # Add to path/visited
                    visited.add((neighbor.x, neighbor.y))
                    path[(neighbor.x, neighbor.y)] = neighbor

                    # Generate directions for this NEW tile
                    new_dirs = self.get_shuffled_directions_toward_goal(neighbor, goal_tile, detour_chance)

                    # Push new context to stack
                    stack.append([neighbor, tile, new_dirs])

                    found_valid_move = True
                    break  # Break the inner loop to process the new tile in the outer loop

            # 3. If no valid moves were found for this tile (Dead End)
            if not found_valid_move:
                # Backtrack: Remove from path and pop from stack
                del path[(tile.x, tile.y)]
                stack.pop()
                # Note: We keep it in 'visited' to prevent revisiting dead ends

        return False

    def _check_tile_validity(self, tile, parent, goal_tile, visited, path):
        """
        Helper to validate if a tile can be stepped onto.
        Returns True if valid, False if invalid.
        """
        # 1. Goal Exception: If it's the goal, it's always valid (even if it's technically a path)
        if tile == goal_tile:
            return True

        # 2. Basic State Checks
        if tile.get_state() in ["path", "border"]:
            return False

        # 3. History Check
        if (tile.x, tile.y) in visited:
            return False

        # 4. Strict Adjacency (The anti-hugging rule)
        if self.check_strict_adjacency(tile, parent, goal_tile, path):
            return False

        # 5. Cluster Check
        if self.check_2x2_path_cluster(tile, path):
            return False

        return True

    def get_shuffled_directions_toward_goal(self, tile, target_tile, detour_chance=0.4):
        """Returns a list of directions toward the goal, shuffled with
        preferred directions first and unpreferred directions after.

        Args:
            tile (Tile): The tile to find neighbors for
            target_tile(Tile): The target tile
            detour_chance (float): Chance of taking a detour

        Returns:
            list: A list of possible moves
        """
        # Get all possible moves
        all_moves = ["up", "right", "down", "left"]

        # obtain general direction towards goal
        dx = target_tile.x - tile.x
        dy = target_tile.y - tile.y

        preferred = []
        if dx > 0:
            preferred.append('right')
        elif dx < 0:
            preferred.append('left')

        if dy > 0:
            preferred.append('up')
        elif dy < 0:
            preferred.append('down')

        unpreferred = [d for d in all_moves if d not in preferred]

        random.shuffle(preferred)
        random.shuffle(unpreferred)

        if random.random() < detour_chance:
            # Randomize, but keep preferred weighted slightly better or fully random
            random.shuffle(all_moves)
            return all_moves
        else:
            return preferred + unpreferred

    def get_neighboring_tile(self, tile, direction):
        """
        Finds the neighboring tile in the given direction.

        Args:
            tile (Tile): The tile to find neighbors for
            direction (str): The direction to find neighbors for

        Returns:
            Tile: The neighboring tile object, or None if out of bounds
        """
        # Calculate potential new coordinates
        nx, ny = tile.x, tile.y

        if direction == "up":
            ny += 1
        elif direction == "right":
            nx += 1
        elif direction == "down":
            ny -= 1
        elif direction == "left":
            nx -= 1

        # VALIDATION: Check if new coordinates are within map dimensions
        if 0 <= nx < self.width and 0 <= ny < self.height:
            return self.map[ny][nx]

        # Return None if we hit a wall
        return None

    def get_surrounding_tiles(self, tile):
        """
        Returns a list of all tiles surrounding the given tile.

        Args:
            tile (Tile): The tile to find neighbors for

        Returns:
            list: A list of all tiles surrounding the given tile [[1 2 3][4 5 6][7 8 9]].flatten
        """
        x = tile.x
        y = tile.y
        res = []
        for row in [-1, 0, 1]:
            for each in [-1, 0, 1]:
                res.append(self.map[y + row][x + each])
        return res

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
                    if neighbor_tile.get_state() != 'empty' or (nx, ny) in path:
                        count += 1

            if count == 4:
                # Placing tile here would form a 2x2 or larger solid cluster
                return True

        return False

    def check_strict_adjacency(self, tile, parent_tile, goal_tile, current_path_dict):
        """
        Ensures a tile does not 'hug' existing paths.
        A tile is valid ONLY if its orthogonal neighbors are clear,
        except for the parent (where we came from) and the goal (where we go).
        """
        # Get orthogonal neighbors (Up, Down, Left, Right)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in directions:
            nx, ny = tile.x + dx, tile.y + dy

            # Check Bounds
            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue

            neighbor = self.map[ny][nx]

            # EXCEPTION 1: Ignore the parent (the tile we just stepped off of)
            if parent_tile and neighbor == parent_tile:
                continue

            # EXCEPTION 2: Ignore the goal (we MUST touch it to finish)
            if neighbor == goal_tile:
                continue

            # CHECK: Is this neighbor an obstacle?
            # 1. Is it part of the OLD map (path/spawn/goal)?
            if neighbor.get_state() in ['path', 'spawn', 'goal']:
                return True  # FAIL: We are hugging an existing path

            # 2. Is it part of the NEW path we are currently generating?
            if (nx, ny) in current_path_dict:
                return True  # FAIL: We are hugging our own tail

        return False
    
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
        points_checked = 0

        # Lower loop limit to prevent freezing
        while points_checked < 10:
            # 1. Find valid empty spot
            new_point = random.choice(random.choice(self.map))

            if self.check_for_border(new_point, dist=SPAWN_GOAL_DISTANCE_FROM_EDGE)[0]:
                continue
            if self.check_spawn_or_goal_nearby(new_point):
                continue

            points_checked += 1

            # 2. Get candidates
            candidates = self.get_candidate_path_points(new_point)
            if not candidates:
                continue

            # --- OPTIMIZATION: Only try the first 5 candidates ---
            # If we can't connect to any of the first 5 random path tiles,
            # this specific 'new_point' is probably in a bad spot. Move on.
            candidates = candidates[:5]

            # 3. Connect
            path_connected = False
            for fork_point in candidates:
                path = self.branch_path_generation(fork_point, new_point)
                if path:
                    path_connected = True
                    break

            if not path_connected:
                continue

            # 4. Finalize
            if pt_type == "spawn":
                new_point.set_state('spawn')
                self.spawns.append(new_point)
            else:
                new_point.set_state('goal')
                self.goals.append(new_point)
            return

        print(f"Could not generate new {pt_type} (Map might be too crowded)")

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def get_candidate_path_points(self, target_point):
        """
        Returns a list of path tiles that are valid starting points for a branch
        directed SPECIFICALLY toward the target_point.
        """
        path_tiles = [tile for row in self.map for tile in row if tile.get_state() == 'path']

        if not path_tiles:
            return []

        scales, _ = get_path_scale_and_detour(self.difficulty)

        max_distance_from_target = max(
            target_point.shortest_path_to(tile) for tile in path_tiles
        )

        min_distance = int((2 - scales[1]) * max_distance_from_target)
        max_distance = int((2 - scales[0]) * max_distance_from_target)

        valid_tiles = []
        for tile in path_tiles:
            distance = target_point.shortest_path_to(tile)
            if min_distance <= distance <= max_distance:
                # --- CHANGE: Pass the target_point to the check ---
                if self.check_valid_branch_start(tile, target_point):
                    valid_tiles.append(tile)

        random.shuffle(valid_tiles)
        return valid_tiles

    def check_valid_branch_start(self, tile, target_tile):
        """
        Checks if a tile is a valid branch start.
        """
        x, y = tile.x, tile.y

        # Determine preferred directions based on target
        preferred_directions = []
        if target_tile.x > x:
            preferred_directions.append((1, 0))
        elif target_tile.x < x:
            preferred_directions.append((-1, 0))
        if target_tile.y > y:
            preferred_directions.append((0, 1))
        elif target_tile.y < y:
            preferred_directions.append((0, -1))

        for dx, dy in preferred_directions:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue

            neighbor = self.map[ny][nx]

            # 1. Must be empty
            if neighbor.get_state() != 'empty':
                continue

            # 2. Strict Adjacency Check for the first step
            # For the first step, the 'tile' (branch point) is the PARENT.
            # We pass an empty dict {} for current_path because the branch hasn't started yet.
            if self.check_strict_adjacency(neighbor, tile, target_tile, {}):
                continue

            # 3. Cluster Check
            temp_path = {(nx, ny): neighbor}
            if self.check_2x2_path_cluster(neighbor, temp_path):
                continue

            return True

        return False

    def branch_path_generation(self, start_tile, end_tile):
        """
        Generates a branching path with a 'Best Effort' fallback.
        Prioritizes short paths over overly long paths if a perfect match isn't found.
        """
        scales, detour_chance = get_path_scale_and_detour(self.difficulty)
        shortest_path_length = start_tile.shortest_path_to(end_tile)

        # Define the allowed range
        min_len = scales[0] * shortest_path_length
        max_len = scales[1] * shortest_path_length

        # TRACKING VARIABLES
        best_path = {}
        best_score = float('inf')  # Lower score is better

        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            visited = set()
            path = {}

            # Run DFS
            path_found = self.recursive_path_helper(end_tile, start_tile, visited, path, detour_chance)

            if path_found:
                current_len = len(path)

                # 1. Perfect Match: Return immediately
                if min_len <= current_len <= max_len:
                    self._finalize_branch(path, start_tile, end_tile)
                    return path

                # 2. Calculate Weighted Score
                score = 0

                if current_len < min_len:
                    # Undershoot: Linear Penalty (1x)
                    # A path 5 tiles too short adds 5 to the score.
                    score = (min_len - current_len)
                else:
                    # Overshoot: Heavy Multiplier Penalty (3x)
                    # A path 5 tiles too long adds 15 to the score.
                    # This makes the algorithm HATE long paths.
                    score = (current_len - max_len) * 3

                # 3. Compare to best
                if score < best_score:
                    best_score = score
                    best_path = path.copy()

            attempts += 1

        # Fallback: If we found ANY path, use the best one
        if best_path:
            self._finalize_branch(best_path, start_tile, end_tile)
            return best_path

        return {}

    def _finalize_branch(self, path, start_tile, end_tile):
        """Helper to color the path correctly after generation."""
        for t in path.values():
            if t.get_state() not in ['spawn', 'goal']:
                t.set_state('path')

        # Restore Start/End states just in case
        if start_tile in self.spawns:
            start_tile.set_state('spawn')
        elif start_tile in self.goals:
            start_tile.set_state('goal')

        if end_tile.get_state() == 'path': end_tile.set_state('path')

    def get_path_bfs(self, start_tile, end_tile):
        """
        Finds a path from start_tile to end_tile using Breadth-First Search.
        It strictly follows tiles marked as 'path', 'spawn', or 'goal'.

        Returns:
            list[Tile]: A list of Tile objects representing the path.
        """
        # Queue stores tuples of (current_tile, current_path_list)
        queue = [(start_tile, [start_tile])]
        visited = {start_tile}

        while queue:
            current_tile, path = queue.pop(0)

            # Found the destination? Return the path.
            if current_tile == end_tile:
                return path

            # Check all 4 orthogonal neighbors
            for direction in ["up", "right", "down", "left"]:
                neighbor = self.get_neighboring_tile(current_tile, direction)

                # 1. Check bounds and if visited
                if not neighbor or neighbor in visited:
                    continue

                # 2. Check if walkable
                # We can only walk on Path, Spawn, or Goal tiles.
                # We CANNOT walk on Empty or Border tiles.
                valid_states = ['path', 'spawn', 'goal']
                if neighbor.get_state() in valid_states:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))

        print("BFS Failed: No connected path of 'path' tiles found between start and end.")
        return None

    def calculate_autotiling(self):
        """
        Iterates over the map and assigns a specific texture variation
        to path tiles based on their neighbors.
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.map[y][x]

                # We only care about making 'path' tiles look like tunnels
                # Note: You might also want to include 'spawn' and 'goal' in this look
                if tile.get_state() not in ['path', 'spawn', 'goal']:
                    continue

                # Calculate the Bitmask
                # North=1, East=2, South=4, West=8
                mask = 0

                # Check North
                n = self.get_neighboring_tile(tile, "up")
                if n and n.get_state() in ['path', 'spawn', 'goal']:
                    mask += 1

                # Check East
                e = self.get_neighboring_tile(tile, "right")
                if e and e.get_state() in ['path', 'spawn', 'goal']:
                    mask += 2

                # Check South
                s = self.get_neighboring_tile(tile, "down")
                if s and s.get_state() in ['path', 'spawn', 'goal']:
                    mask += 4

                # Check West
                w = self.get_neighboring_tile(tile, "left")
                if w and w.get_state() in ['path', 'spawn', 'goal']:
                    mask += 8

                # Save this mask to the tile so it knows which image to load
                tile.set_bitmask(mask)



