import arcade
import arcade.gui
from src.constants import *
from src.managers.sound_manager import SoundManager


class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()
        self.sound_manager = SoundManager()

        # Root Layout
        self.root_layout = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root_layout)

        # Vertical Box to stack everything
        self.v_box = arcade.gui.UIBoxLayout(vertical=True, space_between=20)

        # 1. Title
        title = arcade.gui.UILabel(
            text="MISSION BRIEFING",
            font_size=30,
            font_name="Kenney Future",
            text_color=arcade.color.GOLD,
            align="center"
        )
        self.v_box.add(title)

        # 2. Lore / Intro (Centered)
        lore_str = (
            "The steam tunnels underneath UT Austin have been breached.\n"
            "Former Students, now zombies are swarming the infrastructure.\n\n"
            "Your mission: Construct defenses and protect the Main Boiler\n"
            "at all costs. Do not let them reach the exit.\n"
            "Be prepared as new openings and exits are added."
        )

        # --- FIX: Use UILabel with align="center" ---
        lore = arcade.gui.UILabel(
            text=lore_str,
            width=700,  # Width limits the text wrapping
            font_size=14,
            font_name="Arial",
            text_color=arcade.color.WHITE,
            multiline=True,
            align="center"
        )
        self.v_box.add(lore)

        # 3. Controls List (Centered)
        controls_str = (
            "CONTROLS\n\n"
            "Left Click : Place Tower / Select Tower\n"
            "Hammer Icon : Open Build Menu\n"
            "Arrow Keys : Move Camera\n"
            "P : Pause Game\n"
            "F : Fast Forward (2x)\n"
            "H : Toggle Shaders"
        )

        controls = arcade.gui.UILabel(
            text=controls_str,
            width=700,
            font_size=16,
            font_name="Kenney Future",
            text_color=arcade.color.CYAN,
            multiline=True,
            align="center"
        )
        self.v_box.add(controls)

        # 4. Continue Prompt
        continue_lbl = arcade.gui.UILabel(
            text="CLICK TO DEPLOY",
            font_size=20,
            font_name="Kenney Future",
            text_color=arcade.color.GREEN,
            align="center"
        )

        # Add padding using with_padding (standard in Arcade 3.0)
        self.v_box.add(continue_lbl.with_padding(top=20))

        # Center the whole box on screen
        self.root_layout.add(self.v_box, anchor_x="center", anchor_y="center")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.sound_manager.start_instruction_bg()

    def on_draw(self):
        self.clear()
        self.ui_manager.draw()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """Start the Game when clicked."""
        self.ui_manager.disable()

        self.sound_manager.stop_ambience()
        self.sound_manager.play_sound("ui_start", volume=0.8)

        from src.views.game_view import GameView

        grid_width = self.window.width // TILE_SIZE
        grid_height = self.window.height // TILE_SIZE

        game_view = GameView(grid_width, grid_height, TILE_SIZE)
        self.window.show_view(game_view)