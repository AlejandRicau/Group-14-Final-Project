from constants import *
from helper_functions import *
from Map import Map
from Tile import Tile
from Enemy import Enemy
from Tower import BaseTower
import arcade
import random
import math


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.tile_size = tile_size
        self.map = Map(width, height)
        self.camera = arcade.camera.Camera2D()

        # --- Sprite Lists ---
        self.background_list = arcade.SpriteList()
        self.tower_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # 1. blocking_sprites: Holds the actual tile sprites that block movement
        self.blocking_sprites = arcade.SpriteList(use_spatial_hash=True)

        # 2. astar_barrier_list: The helper object Arcade needs for pathfinding
        self.astar_barrier_list = None

        # Initial build
        self.rebuild_background_list()

        # Camera control parameters
        self.camera_speed = 20
        self.keys_held = set()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.background_list.draw()
        self.tower_list.draw()
        self.enemy_list.draw()

    def on_update(self, delta_time: float):
        # Update all enemies
        self.enemy_list.update()

        # Smooth camera movement
        dx = dy = 0
        if arcade.key.LEFT in self.keys_held:
            dx -= self.camera_speed
        if arcade.key.RIGHT in self.keys_held:
            dx += self.camera_speed
        if arcade.key.UP in self.keys_held:
            dy += self.camera_speed
        if arcade.key.DOWN in self.keys_held:
            dy -= self.camera_speed

        if dx != 0 or dy != 0:
            x, y = self.camera.position
            self.camera.position = (x + dx, y + dy)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        # --- FIX: Use bottom_left position for camera ---
        # We need the bottom-left corner to convert mouse pixels to world pixels.
        camera_x = self.camera.bottom_left.x
        camera_y = self.camera.bottom_left.y

        world_x = x + camera_x
        world_y = y + camera_y

        # Convert world pixels to grid coordinates
        tx, ty = pixel_to_tile(world_x, world_y, self.tile_size)

        # Bounds check
        if not (0 <= tx < self.map.width and 0 <= ty < self.map.height):
            return

        clicked_tile = self.map.map[ty][tx]

        # Debug print to verify coordinates
        # print(f"Click: ({x}, {y}) -> World: ({world_x}, {world_y}) -> Tile: ({tx}, {ty}) -> State: {clicked_tile.get_state()}")

        if button == arcade.MOUSE_BUTTON_LEFT:
            print(f"clicked tile: {clicked_tile}")
            # Logic 1: Add Tower (If T is held)
            if arcade.key.T in self.keys_held:
                self.add_tower(world_x, world_y)

            # Logic 2: Spawn Enemy (If clicking on a SPAWN tile)
            elif clicked_tile.get_state() == 'spawn':
                self.spawn_enemy_at_tile(clicked_tile)

    def spawn_enemy_at_tile(self, start_tile):
        """
        Creates an enemy at the start_tile, calculates a path to a weighted random goal.
        """
        # 1. Select a goal
        target_goal = self.get_weighted_goal(start_tile)
        if not target_goal:
            print("No reachable goals!")
            return

        # --- FIX 2: Debug Collision Checks ---
        # Create a temp sprite to test collisions at Start and End
        # This tells us immediately if the map logic is blocking our spawns
        tester = arcade.SpriteSolidColor(width=1, height=1, color=arcade.color.WHITE)

        # Check Start
        tester.position = start_tile.position
        if arcade.check_for_collision_with_list(tester, self.blocking_sprites):
            print(f"ERROR: Spawn {start_tile.grid_pos} is inside a barrier!")
            return

        # Check Goal
        tester.position = target_goal.position
        if arcade.check_for_collision_with_list(tester, self.blocking_sprites):
            print(f"ERROR: Goal {target_goal.grid_pos} is inside a barrier!")
            return

        # 2. Calculate Path using Arcade's A*
        path_pixels = arcade.astar_calculate_path(
            start_tile.position,
            target_goal.position,
            self.astar_barrier_list,
            diagonal_movement=False  # Reverting to False based on your orthogonal logic
        )

        if not path_pixels:
            print(f"Error: A* failed. (Start: {start_tile.grid_pos}, End: {target_goal.grid_pos})")
            return

        # 3. Create Enemy
        # FIX: Removed tile_size argument
        enemy = Enemy(path=path_pixels, speed=60)

        self.enemy_list.append(enemy)
        print(f"Spawned enemy. Path length: {len(path_pixels)} steps.")

    def get_weighted_goal(self, start_tile):
        """
        Selects a random goal, but closer goals have a much higher chance
        of being selected.
        """
        if not self.map.goals:
            return None

        goals = self.map.goals
        weights = []

        for goal in goals:
            # Calculate Euclidean distance
            dist = math.sqrt((goal.x - start_tile.x) ** 2 + (goal.y - start_tile.y) ** 2)

            # Inverse distance weight: Closer = Higher weight
            # Add a small epsilon (0.1) to prevent division by zero if dist is 0
            weight = 1 / (dist + 0.1)

            # Raise to power to make preference for closer goals stronger (weight squared)
            weights.append(weight ** 2)

        # Select one goal based on weights
        selected_goal = random.choices(goals, weights=weights, k=1)[0]
        return selected_goal

    def rebuild_background_list(self):
        """
        Rebuilds the sprite list for rendering AND the AStarBarrierList for pathfinding.
        """
        self.background_list.clear()

        # --- FIX 1: Re-create the list entirely to clear stale Spatial Hash data ---
        self.blocking_sprites = arcade.SpriteList(use_spatial_hash=True)

        for row in self.map.map:
            for tile in row:
                tile.update_texture()
                self.background_list.append(tile)

                # If a tile is NOT walkable, it is a barrier.
                # We EXPLICITLY check the state to be sure.
                state = tile.get_state()
                if state not in ['path', 'spawn', 'goal']:
                    self.blocking_sprites.append(tile)

        # Create a tiny 1x1 dummy enemy for path calculation
        dummy_enemy = arcade.SpriteSolidColor(width=1, height=1, color=arcade.color.WHITE)

        self.astar_barrier_list = arcade.AStarBarrierList(
            moving_sprite=dummy_enemy,
            blocking_sprites=self.blocking_sprites,
            grid_size=self.tile_size,
            left=0,
            right=self.map.width * self.tile_size,
            bottom=0,
            top=self.map.height * self.tile_size
        )

    def add_tower(self, mouse_x, mouse_y):
        """
        Adds a tower to the map at the tile hovered by the mouse.
        """
        # convert mouse position to tile position and find the tile_curr
        tx, ty = pixel_to_tile(mouse_x, mouse_y, self.tile_size)
        tile_hovered = self.map.map[ty][tx]

        # check validity
        if not self.is_valid_tower_location(tile_hovered):
            return

        # add tower
        tower = BaseTower(tile_hovered)
        self.tower_list.append(tower)

    def is_valid_tower_location(self, tile):
        """
        Returns True if the tile is a valid location for a tower.
        """
        valid = False

        # check if the tile is next to a path
        surrounding_tiles = self.map.get_surrounding_tiles(tile)
        for idx, t in enumerate(surrounding_tiles):
            if idx == len(surrounding_tiles) // 2:  # the tile hovered
                if t.get_state() != 'empty':  # the tile hovered must be empty
                    return False
            if t.get_state() == 'path':  # must be adjacent to path
                valid = True
        return valid

    def on_key_press(self, symbol, modifiers):
        self.keys_held.add(symbol)

        if symbol == arcade.key.M:
            self.map.generate_new_map()
            self.rebuild_background_list()
            self.tower_list.clear()
            self.enemy_list.clear()  # Clear enemies on new map

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0]
            )
            self.rebuild_background_list()
            self.enemy_list.clear()  # Paths changed, enemies invalid

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6, add_new_spawns_goals=False)
            self.rebuild_background_list()
            self.tower_list.clear()  # Towers might be misplaced on expand
            self.enemy_list.clear()

        elif symbol == arcade.key.F:
            self.map.generate_new_special_point("spawn")
            self.rebuild_background_list()

        elif symbol == arcade.key.G:
            self.map.generate_new_special_point("goal")
            self.rebuild_background_list()

        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_held:
            self.keys_held.remove(symbol)


def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()