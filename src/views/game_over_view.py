import arcade
from src.constants import *


class GameOverView(arcade.View):
    def __init__(self, wave_reached, money_earned):
        super().__init__()
        self.wave_reached = wave_reached
        self.money_earned = money_earned

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "GAME OVER",
            self.window.width / 2, self.window.height / 2 + 60,
            arcade.color.RED, font_size=50, anchor_x="center", font_name="Kenney Future"
        )

        arcade.draw_text(
            f"You survived until Wave {self.wave_reached}",
            self.window.width / 2, self.window.height / 2,
            arcade.color.WHITE, font_size=20, anchor_x="center", font_name="Kenney Future"
        )

        arcade.draw_text(
            f"Total Wealth: ${self.money_earned}",
            self.window.width / 2, self.window.height / 2 - 30,
            arcade.color.GOLD, font_size=20, anchor_x="center", font_name="Kenney Future"
        )

        arcade.draw_text(
            "Click to Restart",
            self.window.width / 2, self.window.height / 2 - 80,
            arcade.color.GRAY, font_size=15, anchor_x="center", font_name="Kenney Future"
        )

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Import locally to avoid circular imports
        from src.views.start_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)