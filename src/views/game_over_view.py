import arcade
from src.constants import *
from src.managers.game_manager import GameManager


class GameOverView(arcade.View):
    def __init__(self, wave_reached, money_earned):
        super().__init__()
        self.wave_reached = wave_reached
        self.money_earned = money_earned

        self.camera = arcade.camera.Camera2D()

        # --- FIX: Save Waves as High Score ---
        gm = GameManager()
        is_new_record = gm.save_high_score(self.wave_reached)
        high_score = gm.high_score

        center_x = self.window.width / 2
        center_y = self.window.height / 2

        self.title_text = arcade.Text(
            "GAME OVER",
            center_x, center_y + 80,
            arcade.color.RED, font_size=50, anchor_x="center", font_name="Kenney Future"
        )

        # --- NEW: High Score Display (Waves) ---
        if is_new_record:
            hs_text = f"NEW RECORD! Wave {self.wave_reached}"
            hs_color = arcade.color.CYAN
        else:
            hs_text = f"Best Run: Wave {high_score}"
            hs_color = arcade.color.GRAY

        self.hs_text = arcade.Text(
            hs_text,
            center_x, center_y + 20,
            hs_color, font_size=24, anchor_x="center", font_name="Kenney Future"
        )

        self.wave_text = arcade.Text(
            f"You reached Wave {self.wave_reached}",
            center_x, center_y - 20,
            arcade.color.WHITE, font_size=20, anchor_x="center", font_name="Kenney Future"
        )

        self.restart_text = arcade.Text(
            "Click to Restart",
            center_x, center_y - 100,
            arcade.color.WHITE, font_size=15, anchor_x="center", font_name="Kenney Future"
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.title_text.draw()
        self.hs_text.draw()
        self.wave_text.draw()
        self.restart_text.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        from src.views.start_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)