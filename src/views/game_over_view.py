import arcade
from src.constants import *

class GameOverView(arcade.View):
    def __init__(self, wave_reached, money_earned):
        super().__init__()
        self.wave_reached = wave_reached
        self.money_earned = money_earned

        # Create a Camera for the UI
        self.camera = arcade.camera.Camera2D()

        # --- PERFORMANCE FIX: Create Text objects once ---
        center_x = self.window.width / 2
        center_y = self.window.height / 2

        self.title_text = arcade.Text(
            "GAME OVER",
            center_x, center_y + 60,
            arcade.color.RED,
            font_size=50,
            anchor_x="center",
            font_name="Kenney Future"
        )

        self.wave_text = arcade.Text(
            f"You survived until Wave {self.wave_reached}",
            center_x, center_y,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
            font_name="Kenney Future"
        )

        self.money_text = arcade.Text(
            f"Total Wealth: ${self.money_earned}",
            center_x, center_y - 30,
            arcade.color.GOLD,
            font_size=20,
            anchor_x="center",
            font_name="Kenney Future"
        )

        self.restart_text = arcade.Text(
            "Click to Restart",
            center_x, center_y - 80,
            arcade.color.GRAY,
            font_size=15,
            anchor_x="center",
            font_name="Kenney Future"
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.camera.use()

        # --- PERFORMANCE FIX: Draw the objects ---
        self.title_text.draw()
        self.wave_text.draw()
        self.money_text.draw()
        self.restart_text.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        from src.views.start_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)