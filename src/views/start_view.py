import arcade
from src.constants import *

class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        # Create a Camera for the UI
        self.camera = arcade.camera.Camera2D()

        # --- PERFORMANCE FIX: Create Text objects once ---
        self.title_text = arcade.Text(
            "STEAM TUNNELS DEFENSE",
            self.window.width / 2,
            self.window.height / 2 + 50,
            arcade.color.GOLD,
            font_size=40,
            anchor_x="center",
            font_name="Kenney Future"
        )

        self.instruction_text = arcade.Text(
            "Click to Start",
            self.window.width / 2,
            self.window.height / 2 - 30,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            font_name="Kenney Future"
        )

    def on_show_view(self):
        """Called when switching to this view."""
        arcade.set_background_color(COLOR_BACKGROUND)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # --- PERFORMANCE FIX: Draw the pre-generated objects ---
        self.title_text.draw()
        self.instruction_text.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """If the user presses the mouse button, start the game."""
        from src.views.game_view import GameView

        grid_width = self.window.width // TILE_SIZE
        grid_height = self.window.height // TILE_SIZE

        game_view = GameView(grid_width, grid_height, TILE_SIZE)
        self.window.show_view(game_view)