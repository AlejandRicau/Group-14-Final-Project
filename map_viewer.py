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
        self.range_display_list = arcade.SpriteList()

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
        self.range_display_list.draw()

    def on_update(self, delta_time: float):
        # Update all enemies
        self.enemy_list.update()

        # Update tower detection


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
        """Functional response of mouse press"""

        # convert mouse pos to world pos
        world_point = self.camera.unproject((x, y))
        world_x, world_y, _ = world_point  # `unproject` returns a Vec3

        # get the tile on the position
        clicked_tile = arcade.get_sprites_at_point((world_x, world_y), self.background_list)[0]

        # mouse left click
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Debug print to verify coordinates
            print(f"clicked tile: {clicked_tile}", end = "  ")
            print(f"Tower: {bool(clicked_tile.tower)}")

            # Logic 1: Add Tower (If T is held)
            if arcade.key.T in self.keys_held:
                if not clicked_tile.tower:
                    self.add_tower(clicked_tile)
                else:
                    clicked_tile.tower.toggle_range_display()

            # Logic 2: Spawn Enemy (If clicking on a SPAWN tile)
            elif clicked_tile.get_state() == 'spawn':
                self.spawn_enemy_at_tile(clicked_tile)

    def on_key_press(self, symbol, modifiers):
        self.keys_held.add(symbol)

        if symbol == arcade.key.M:
            self.map.generate_new_map()
            self.rebuild_background_list()
            self.tower_list.clear()
            self.enemy_list.clear()
            self.range_display_list.clear()

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0]
            )
            self.map.calculate_autotiling()
            self.rebuild_background_list()
            self.enemy_list.clear()  # Paths changed, enemies invalid

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6, add_new_spawns_goals=False)
            self.map.calculate_autotiling()
            self.rebuild_background_list()
            self.enemy_list.clear()

        elif symbol == arcade.key.F:
            self.map.generate_new_special_point("spawn")
            self.map.calculate_autotiling()
            self.rebuild_background_list()

        elif symbol == arcade.key.G:
            self.map.generate_new_special_point("goal")
            self.map.calculate_autotiling()
            self.rebuild_background_list()

        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_held:
            self.keys_held.remove(symbol)


    def spawn_enemy_at_tile(self, start_tile):
        """
        Creates an enemy at the start_tile using internal BFS pathfinding.
        """
        # 1. Select a goal
        target_goal = self.get_weighted_goal(start_tile)
        if not target_goal:
            print("No reachable goals!")
            return

        # 2. Calculate Path using OUR OWN BFS (No Physics/Hitboxes involved)
        # This returns a list of Tile objects
        path_tiles = self.map.get_path_bfs(start_tile, target_goal)

        if not path_tiles:
            print(f"Error: No path found between {start_tile.grid_pos} and {target_goal.grid_pos}")
            return

        # 3. Convert Tile objects to Pixel Coordinates for the Enemy class
        # The Enemy needs [(x,y), (x,y)...] to move.
        path_pixels = [(t.center_x, t.center_y) for t in path_tiles]

        # 4. Create Enemy
        enemy = Enemy(path=path_pixels, speed=60)

        self.enemy_list.append(enemy)
        print(f"Spawned enemy. Steps: {len(path_pixels)}")

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
            # Calculate distance
            dist = len(self.map.get_path_bfs(start_tile, goal))**1.5
            weights.append(dist)

        # Select one goal based on weights
        weights = [1 / w for w in weights]
        selected_goal = random.choices(goals, weights=weights, k=1)[0]
        return selected_goal

    def rebuild_background_list(self):
        """
        Rebuilds the sprite list for rendering
        """
        self.background_list.clear()
        self.tower_list.clear()
        self.range_display_list.clear()

        for row in self.map.map:
            for tile in row:
                tile.update_texture()
                self.background_list.append(tile)
                if tile.tower:
                    tile.tower.update()
                    self.tower_list.append(tile.tower)
                    self.range_display_list.append(tile.tower.range_display)


    def add_tower(self, tile):
        """
        Adds a tower to the map at the tile hovered by the mouse.
        """
        # check validity
        if not self.is_valid_tower_location(tile):
            return

        # add tower and link it to the tile
        tower = BaseTower(tile)
        tile.link_tower(tower)

        # add tower to the tower list
        self.tower_list.append(tower)
        self.range_display_list.append(tower.range_display)


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

    def update_tower_detection(self):
        """
        Updates the tower's target enemy.
        """

        # iterate through each tower
        for tower in self.tower_list:

            # check if any enemy is in range
            enemies_in_range = arcade.check_for_collision_with_list(
                tower.range_display,  # the range sprite
                self.enemy_list  # the SpriteList of enemies
            )

            # if no enemy is in range, reset the tower's target
            if not enemies_in_range:
                tower.on_target = None
                tower.range_display.color = arcade.color.GRAY
                continue

            # if there are multiple enemies in range, find the closest one
            dist = float('inf')
            closest = None
            for enemy in enemies_in_range:

                # calculate distance
                curr_dist = distance_measure(
                        tower.center_x, tower.center_y,
                        enemy.center_x, enemy.center_y
                    )

                # if this is the first enemy or this enemy is closer, update closest
                if (not closest) or (curr_dist < dist):
                    closest = enemy
                    dist = curr_dist

            tower.on_target = closest
            tower.range_display.color = arcade.color.GRAY



def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()