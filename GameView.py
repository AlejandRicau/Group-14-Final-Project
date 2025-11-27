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
from WaveManager import WaveManager


class GameView(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(COLOR_BACKGROUND)

        self.tile_size = tile_size
        self.map = Map(width, height)

        # Game Managers
        self.game_manager = GameManager()
        self.wave_manager = WaveManager(self)

        # Tower to place
        self.selected_tower_type = None

        # --- UI Setup ---
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.setup_ui()

        # Create the variables to hold our labels so we can update them later
        self.money_label = None
        self.lives_label = None
        self.wave_label = None
        self.ui_layout = None

        self.setup_ui()  # Helper function to build the layout

        # Sprite Lists
        self.camera = arcade.camera.Camera2D()
        self.background_list = arcade.SpriteList()
        self.tower_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.range_display_list = arcade.SpriteList()
        self.bar_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
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
        """Builds the Top Bar and the Collapsible Sidebar."""
        self.ui_manager.clear()

        # Root Layout covering the whole screen
        self.root_layout = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root_layout)

        # ==================================================
        # 1. TOP BAR (Stats) - Compact Version
        # ==================================================

        # Load Textures
        icon_money = arcade.load_texture(":resources:images/items/coinGold.png")
        icon_lives = arcade.load_texture(":resources:images/items/gemRed.png")

        # Helper: Tighter spacing for compact look
        def create_stat_group(icon, text, color):
            # Reduced icon size from 24 to 16
            img = arcade.gui.UIImage(texture=icon, width=16, height=16)
            lbl = arcade.gui.UILabel(
                text=text,
                font_size=14,  # Slightly smaller font
                font_name="Kenney Future",
                text_color=color
            )
            # Reduced spacing from 5 to 2
            box = arcade.gui.UIBoxLayout(vertical=False, space_between=2, align="center")
            box.add(img)
            box.add(lbl)
            return box, lbl

        # Create Groups
        grp_money, self.money_label = create_stat_group(icon_money, str(self.game_manager.money), arcade.color.GOLD)
        grp_lives, self.lives_label = create_stat_group(icon_lives, str(self.game_manager.lives), arcade.color.RED)

        self.wave_label = arcade.gui.UILabel(
            text="Wave: 0",
            font_size=14,
            font_name="Kenney Future",
            text_color=arcade.color.CYAN
        )

        # Combine into horizontal bar with reduced spacing (15 instead of 30)
        top_bar_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)
        top_bar_box.add(grp_money)
        top_bar_box.add(grp_lives)
        top_bar_box.add(self.wave_label)

        # Tighter padding (top/bottom 5 instead of 10)
        top_bar_container = top_bar_box.with_padding(top=5, bottom=5, left=10, right=10)
        top_bar_container = top_bar_container.with_background(color=(0, 0, 0, 150))

        # Add border
        top_bar_container = top_bar_container.with_border(width=2, color=arcade.color.DARK_GRAY)

        # Anchor to Top Center
        self.root_layout.add(top_bar_container, anchor_x="center", anchor_y="top")

        # ==================================================
        # 2. COLLAPSIBLE SIDEBAR (Tower Selection)
        # ==================================================

        # A. The Tower Selection Panel (Hidden by default)
        self.tower_box = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        def create_tower_btn(tower_type, label, cost):
            # Using FlatButton for the list items
            btn = arcade.gui.UIFlatButton(text=f"{label} (${cost})", width=120, height=40)

            @btn.event("on_click")
            def on_click_tower(event):
                self.selected_tower_type = tower_type

                # --- NEW: Create the Ghost Sprite immediately ---
                # This ensures we don't have to load textures in on_draw
                self.create_ghost_tower(tower_type)

            return btn

        self.tower_box.add(create_tower_btn("base", "Base", TOWER_COST))
        self.tower_box.add(create_tower_btn("AOE", "AOE", TOWER_COST))
        self.tower_box.add(create_tower_btn("laser", "Laser", TOWER_COST))

        # Background for the panel
        self.tower_panel = self.tower_box.with_padding(all=10)
        self.tower_panel = self.tower_panel.with_background(color=(0, 0, 0, 180))

        # B. The Hammer Button (Texture Button)
        # We load a hammer texture (using a built-in key texture as a placeholder if hammer isn't available,
        # or you can use :resources:images/items/hammer.png if available, but let's use a generic tool icon)

        # NOTE: Arcade resources doesn't have a "Hammer" icon specifically in the default set.
        # We will use 'wrench.png' from items, or you can providing your own path.
        # Let's use the 'wrench' as the build tool for now.
        hammer_texture = generate_build_icon()

        # Create a Texture Button
        toggle_btn = arcade.gui.UITextureButton(
            texture=hammer_texture,
            width=64, height=64  # Made slightly bigger for touch target
        )

        @toggle_btn.event("on_click")
        def on_toggle_click(event):
            if self.tower_panel in self.root_layout.children:
                self.root_layout.remove(self.tower_panel)
            else:
                # Add panel ABOVE the button (since button is at bottom)
                self.root_layout.add(
                    self.tower_panel,
                    anchor_x="right",
                    anchor_y="bottom",
                    align_y=70,  # Push it up above the hammer
                    align_x=-20
                )

        # Anchor Button to Bottom Right
        self.root_layout.add(toggle_btn, anchor_x="right", anchor_y="bottom", align_x=-20, align_y=20)

    def update_ui_values(self):
        """Updates the text of the labels."""
        self.money_label.text = str(self.game_manager.money)
        self.lives_label.text = str(self.game_manager.lives)

        # --- FIXED: Use update_font() to change color ---
        if self.wave_manager.state == "BETWEEN_WAVES":
            time_left = int(self.wave_manager.timer) + 1
            self.wave_label.text = f"Next Wave: {time_left}s"

            # Use this method instead of .label.color
            self.wave_label.update_font(font_color=arcade.color.GRAY)
        else:
            self.wave_label.text = f"Wave: {self.wave_manager.current_wave}"

            # Use this method instead of .label.color
            self.wave_label.update_font(font_color=arcade.color.CYAN)

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



        # --- NEW: Draw "Ghost" cursor if building ---
        if self.selected_tower_type and len(self.ghost_list) > 0:
            # Update Position
            wx, wy, _ = self.camera.unproject((self._mouse_x, self._mouse_y))
            self.ghost_sprite.position = (wx, wy)

            # Draw the LIST
            self.ghost_list.draw()

            # 2. Draw UI
        self.ui_manager.draw()

    def create_ghost_tower(self, tower_type):
        """Creates a semi-transparent sprite for placement preview."""

        # 1. Clear any old ghosts
        self.ghost_list.clear()

        # 2. Get Texture
        if tower_type in TOWER_TEXTURES:
            tex = TOWER_TEXTURES[tower_type]
        else:
            tex = TOWER_TEXTURES.get("base")

        # 3. Create Sprite (Pass texture as first arg!)
        self.ghost_sprite = arcade.Sprite(tex)
        self.ghost_sprite.alpha = 128

        # 4. Add to the list
        self.ghost_list.append(self.ghost_sprite)

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
        self.wave_manager.update(delta_time)
        self.update_ui_values()

        # Handle camera movement
        self.handle_camera_movement()

    def on_mouse_press(self, x, y, button, modifiers):
        """Handles tower placement based on selected state."""

        # 1. If we clicked the UI, do NOT place a tower on the map
        # Arcade's UIManager doesn't strictly block clicks, but we can check logic
        # Ideally, we rely on the fact that the map is behind the UI.

        # 2. Check if we have a tower selected
        if self.selected_tower_type is None:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            # convert mouse pos to world pos
            world_point = self.camera.unproject((x, y))
            world_x, world_y, _ = world_point

            # Get sprites at point
            sprites = arcade.get_sprites_at_point((world_x, world_y), self.background_list)

            if sprites:
                clicked_tile = sprites[0]
                success = self.try_place_tower(clicked_tile, self.selected_tower_type)

                if success:
                    self.selected_tower_type = None

                    # --- NEW: Clear the list ---
                    self.ghost_list.clear()

    def try_place_tower(self, tile, t_type="base"):
        """Returns True if successful, False otherwise."""
        if tile.tower:
            print("Space occupied!")
            return False

        if not self.game_manager.can_afford(TOWER_COST):  # You might want different costs per type later
            print("Not enough money!")
            return False

        if not tile.is_valid_tower_location(self.map):
            print("Invalid location!")
            return False

        self.add_tower(tile, t_type)
        self.game_manager.spend_money(TOWER_COST)
        return True

    def on_key_press(self, symbol, modifiers):
        self.keys_held.add(symbol)

        if symbol == arcade.key.ESCAPE:
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


    def spawn_enemy_at_tile(self, start_tile, speed=30):
        """
        Creates an enemy at the start_tile using internal BFS pathfinding.
        """
        target_goal = self.get_weighted_goal(start_tile)
        if not target_goal:
            # If map expanded and logic broke, fallback:
            if self.map.goals: target_goal = self.map.goals[0]
            else: return

        path_tiles = self.map.get_path_bfs(start_tile, target_goal)
        if not path_tiles:
            # Try to heal the map if path is missing
            self.map.recursive_path_generation(start_tile, target_goal)
            path_tiles = self.map.get_path_bfs(start_tile, target_goal)
            if not path_tiles: return

        path_pixels = [(t.center_x, t.center_y) for t in path_tiles]

        enemy = Enemy(
            path=path_pixels,
            game_manager=self.game_manager,
            bar_list=self.bar_list,
            speed=speed # <--- Use the speed passed from WaveManager
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
    window =GameView(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()