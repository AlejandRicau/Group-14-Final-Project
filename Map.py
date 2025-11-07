from constants import *

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.generate_new_map()

    def generate_new_map(self):
        """Completely resets the map with new spawn and goal locations."""
        self.map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.spawn_x = random.randint(0, self.width - 1)
        self.spawn_y = random.randint(0, self.height - 1)
        self.goal_x = random.randint(0, self.width - 1)
        self.goal_y = random.randint(0, self.height - 1)
        self.map[self.spawn_y][self.spawn_x] = 2
        self.map[self.goal_y][self.goal_x] = 3

    def generate_random_path(self, detour_chance=0.3):
        """Generates a random perpendicular path from spawn to goal with detours."""
        # Reset map but keep spawn/goal
        self.map = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.map[self.spawn_y][self.spawn_x] = 2
        self.map[self.goal_y][self.goal_x] = 3

        x, y = self.spawn_x, self.spawn_y

        max_steps = self.width * self.height * 2
        steps = 0

        while (x, y) != (self.goal_x, self.goal_y) and steps < max_steps:
            steps += 1
            self.map[y][x] = 1  # mark as path

            dx = self.goal_x - x
            dy = self.goal_y - y

            # Possible perpendicular moves
            possible_moves = []
            if x > 0:
                possible_moves.append((-1, 0))
            if x < self.width - 1:
                possible_moves.append((1, 0))
            if y > 0:
                possible_moves.append((0, -1))
            if y < self.height - 1:
                possible_moves.append((0, 1))

            # Prefer moves toward the goal
            preferred = []
            if dx > 0:
                preferred.append((1, 0))
            elif dx < 0:
                preferred.append((-1, 0))
            if dy > 0:
                preferred.append((0, 1))
            elif dy < 0:
                preferred.append((0, -1))

            # Sometimes take detours
            if random.random() < detour_chance:
                move = random.choice(possible_moves)
            else:
                if preferred:
                    move = random.choice(preferred)
                else:
                    move = random.choice(possible_moves)

            # Apply move
            nx, ny = x + move[0], y + move[1]

            if 0 <= nx < self.width and 0 <= ny < self.height:
                x, y = nx, ny

        # Ensure spawn and goal remain visible
        self.map[self.spawn_y][self.spawn_x] = 2
        self.map[self.goal_y][self.goal_x] = 3

