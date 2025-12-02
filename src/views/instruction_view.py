import arcade
from src.constants import *
from src.managers.sound_manager import SoundManager


class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.camera = arcade.camera.Camera2D()
        self.sound_manager = SoundManager()

        # Center coordinates
        cx = self.window.width / 2
        cy = self.window.height / 2

        # 1. Title
        self.title_text = arcade.Text(
            "MISSION BRIEFING",
            cx, cy + 200,
            arcade.color.GOLD, font_size=30, anchor_x="center", font_name="Kenney Future"
        )

        # 2. Lore / Intro
        lore_str = (
            "The steam tunnels underneath UT Austin have been breached.\n"
            "Former Students, now zombies are swarming the infrastructure.\n\n"
            "Your mission: Construct defenses and protect the Main Boiler\n"
            "at all costs. Do not let them reach the exit.\n"
            "Be prepared as new openings and exits are added."
        )
        self.lore_text = arcade.Text(
            lore_str,
            cx, cy + 130,
            arcade.color.WHITE, font_size=14, anchor_x="center",
            multiline=True, width=600, align="center", font_name="Arial"  # Arial is easier to read for body text
        )

        # 3. Controls List
        controls_str = (
            "CONTROLS\n\n"
            "Left Click : Place Tower / Select Tower\n"
            "Hammer Icon : Open Build Menu\n"
            "Arrow Keys : Move Camera\n"
            "P : Pause Game\n"
            "F : Fast Forward (2x)\n"
            "H : Turn of Shaders (In case they don't work properly)"
        )
        self.controls_text = arcade.Text(
            controls_str,
            cx, cy - 50,
            arcade.color.CYAN, font_size=16, anchor_x="center",
            multiline=True, width=600, align="center", font_name="Kenney Future"
        )

        # 4. Continue Prompt
        self.continue_text = arcade.Text(
            "CLICK TO DEPLOY",
            cx, cy - 250,
            arcade.color.GREEN, font_size=20, anchor_x="center", font_name="Kenney Future"
        )

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.sound_manager.start_instruction_bg()

    def on_draw(self):
        self.clear()
        self.camera.use()

        self.title_text.draw()
        self.lore_text.draw()
        self.controls_text.draw()
        self.continue_text.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """Start the Game when clicked."""
        self.sound_manager.stop_ambience()
        self.sound_manager.play_sound("ui_start", volume=0.8)
        from src.views.game_view import GameView

        grid_width = self.window.width // TILE_SIZE
        grid_height = self.window.height // TILE_SIZE

        game_view = GameView(grid_width, grid_height, TILE_SIZE)
        self.window.show_view(game_view)