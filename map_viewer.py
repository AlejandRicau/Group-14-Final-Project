from constants import *
from helper_functions import *
from Map import Map
from Tile import Tile
from Enemy import Enemy
from Tower import BaseTower, AOETower, LaserTower
import arcade
import arcade.gui
import random
import math
from GameManager import GameManager


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.tile_size = tile_size
        self.map = Map(width, height)

        # Game Managers
        self.game_manager = GameManager()

        # --- GUI SETUP ---
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()  # Vital: tells Arcade to listen for UI events

        # Create the variables to hold our labels so we can update them later
        self.money_label = None
        self.lives_label = None

        self.setup_ui()  # Helper function to build the layout

        # Sprite Lists
        self.camera = arcade.camera.Camera2D()
        self.background_list = arcade.SpriteList()
        self.tower_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.range_display_list = arcade.SpriteList()
        self.bar_list = arcade.SpriteList()
        self.visual_effect_list = []

        # Initialize Managers
        self.game_manager = GameManager()

        # GUI Camera
        # We use a second camera for the UI so it stays static
        # while the map camera moves around.
        self.gui_camera = arcade.camera.Camera2D()

        # Initial build
        if self.map.spawns and self.map.goals:
            self.map.recursive_path_generation(self.map.spawns[0], self.map.goals[0])
            self.map.calculate_autotiling()

        self.rebuild_background_list()

        # Camera control parameters
        self.camera_speed = 20
        self.keys_held = set()

    def setup_ui(self):
        """Creates the UI widgets and layout with Icons and a Background."""

        # 1. Load Textures for Icons (Using built-in resources for now)
        # You can replace these strings with paths to your own images
        icon_money = arcade.load_texture(":resources:images/items/coinGold.png")
        icon_lives = arcade.load_texture(":resources:images/items/gemRed.png")  # Using a red gem as a 'heart' proxy

        # 2. Create the Layout
        self.ui_layout = arcade.gui.UIAnchorLayout()

        # --- HELPER: Create a "Stat Group" (Icon + Label) ---
        def create_stat_group(icon_texture, label_text, text_color):
            # The Icon
            icon_widget = arcade.gui.UIImage(
                texture=icon_texture,
                width=32, height=32
            )

            # The Label
            label_widget = arcade.gui.UILabel(
                text=label_text,
                font_size=20,
                font_name="Kenney Future",
                text_color=text_color
            )

            # Combine them horizontally
            group = arcade.gui.UIBoxLayout(vertical=False, space_between=10, align="center")
            group.add(icon_widget)
            group.add(label_widget)

            return group, label_widget

        # 3. Create Money Group
        money_group, self.money_label = create_stat_group(
            icon_money,
            str(self.game_manager.money),
            arcade.color.GOLD
        )

        # 4. Create Lives Group
        lives_group, self.lives_label = create_stat_group(
            icon_lives,
            str(self.game_manager.lives),
            arcade.color.RED
        )

        # 5. Combine Stats into one main container
        stats_box = arcade.gui.UIBoxLayout(vertical=False, space_between=30)
        stats_box.add(money_group)
        stats_box.add(lives_group)

        # 6. Add Background and Padding (The "Pretty" part)
        # We wrap the stats_box in a container that has a background color
        stats_container = stats_box.with_padding(top=10, bottom=10, left=20, right=20)

        # Add a dark semi-transparent background
        stats_container = stats_container.with_background(
            color=(0, 0, 0, 150)  # Black with alpha 150
        )

        # Add a border (optional)
        stats_container = stats_container.with_border(width=2, color=arcade.color.WHITE)

        # 7. Add to screen (Top Left or Bottom Left)
        self.ui_layout.add(
            child=stats_container,
            anchor_x="left",
            anchor_y="bottom",
            align_x=20,
            align_y=20
        )

        self.ui_manager.add(self.ui_layout)

    def update_ui_values(self):
        """Updates the text of the labels."""
        # Just set the number, the icon provides the context!
        self.money_label.text = str(self.game_manager.money)
        self.lives_label.text = str(self.game_manager.lives)

    def on_draw(self):
        self.clear()

        # 1. Draw World
        self.camera.use()
        self.background_list.draw()
        self.tower_list.draw()
        self.enemy_list.draw()
        self.bar_list.draw()
        self.range_display_list.draw()

        # Draw visual effects
        for vis in self.visual_effect_list:
            vis.draw()

        # Draw hitboxes
        # for enemy in self.enemy_list:
        #     enemy.draw_hit_box()

        # 2. Draw UI
        # The UIManager handles the camera/viewport automatically!
        self.ui_manager.draw()

    def on_update(self, delta_time: float):
        # Update all enemies
        self.enemy_list.update()

        # Update all towers
        self.tower_list.update()

        # Update tower detection
        for tower in self.tower_list:
            tower.acquire_target(self.enemy_list)
            tower.attack_update(delta_time, self.visual_effect_list)

        # Update visual effects
        for vis in self.visual_effect_list[:]:
            vis.update(delta_time)
            if vis.can_be_removed:
                self.visual_effect_list.remove(vis)

        # Update UI Values
        self.update_ui_values()

        # Handle camera movement
        self.handle_camera_movement()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Functional response of mouse press

        Args:
            x (int): x position of mouse
            y (int): y position of mouse
            button (int): button pressed
            modifiers (int): modifiers pressed
        """

        # convert mouse pos to world pos
        world_point = self.camera.unproject((x, y))
        world_x, world_y, _ = world_point  # `unproject` returns a Vec3

        # get the tile on the position
        clicked_tile = arcade.get_sprites_at_point(
            (world_x, world_y),
            self.background_list
        )[0]

        # mouse left click
        if button == arcade.MOUSE_BUTTON_LEFT:
            if arcade.key.KEY_1 in self.keys_held:
                # Try to place a tower
                self.try_place_tower(clicked_tile, t_type="base")

            elif arcade.key.KEY_2 in self.keys_held:
                # Try to place an AOE tower
                self.try_place_tower(clicked_tile, t_type="AOE")

            elif arcade.key.KEY_3 in self.keys_held:
                # Try to place a Laser tower
                self.try_place_tower(clicked_tile, t_type="laser")

            elif clicked_tile.get_state() == "spawn":
                # Spawn enemy if spawn tile clicked
                self.spawn_enemy_at_tile(clicked_tile)

    def on_key_press(self, symbol, modifiers):
        self.keys_held.add(symbol)

        if symbol == arcade.key.M:
            self.map.generate_new_map()
            self.rebuild_background_list()
            self.tower_list.clear()
            self.enemy_list.clear()
            self.bar_list.clear()
            self.range_display_list.clear()

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0]
            )
            self.map.calculate_autotiling()
            self.rebuild_background_list()
            self.tower_list.clear()
            self.enemy_list.clear()  # Paths changed, enemies invalid

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6)
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

    def handle_camera_movement(self):
        dx = (
                (-self.camera_speed if arcade.key.LEFT in self.keys_held else 0)
            +   (self.camera_speed if arcade.key.RIGHT in self.keys_held else 0)
        )
        dy = (
                (self.camera_speed if arcade.key.UP in self.keys_held else 0)
            +   (-self.camera_speed if arcade.key.DOWN in self.keys_held else 0)
        )

        if dx or dy:
            x, y = self.camera.position
            self.camera.position = (x + dx, y + dy)

    def try_place_tower(self, tile, t_type="base"):
        """
        Tries to place a tower at the given tile.

        Args:
            tile (Tile): The tile to place the tower on.
            t_type (str): The type of tower to place.
        """
        if tile.tower:
            # If tower already exists, toggle range display
            tile.tower.toggle_range_display()
            return

        if not self.game_manager.can_afford(TOWER_COST):
            # check for affordability
            print("Not enough money!")
            return

        if not tile.is_valid_tower_location(self.map):
            # check for validity
            print("Invalid location for a tower, has to be next to path!")
            return

        # add tower and spend money
        self.add_tower(tile, t_type)
        self.game_manager.spend_money(TOWER_COST)
        print(f"Tower placed! Remaining Money: {self.game_manager.money}")

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
        enemy = Enemy(
            path=path_pixels,
            game_manager=self.game_manager,
            bar_list=self.bar_list,  # <--- Pass the list here
            speed=30
        )

        self.enemy_list.append(enemy)


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
            path = self.map.get_path_bfs(start_tile, goal)

            # Safety check: If path is None (disconnected), skip this goal
            if path is None:
                continue

            dist = len(path) ** 1.5
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
                    self.range_display_list.append(tile.tower.target_dot)


    def add_tower(self, tile, t_type="base"):
        """
        Adds a tower to the map at the tile hovered by the mouse.
        """
        # define tower based on type
        if t_type == "base":
            tower = BaseTower(tile)

        elif t_type == "AOE":
            tower = AOETower(tile)

        elif t_type == "laser":
            tower = LaserTower(tile)

        else:
            print("Invalid tower type!")
            return

        # add tower and link it to the tile
        tile.link_tower(tower)

        # add tower to the tower list
        self.tower_list.append(tower)
        self.range_display_list.append(tower.range_display)
        self.range_display_list.append(tower.target_dot)



def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()