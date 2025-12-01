import arcade
from pathlib import Path

# Dynamic Path Setup
CURRENT_FILE_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_FILE_DIR.parent.parent
SOUND_DIR = PROJECT_ROOT / "assets" / "sounds"


class SoundManager:
    def __init__(self):
        # Dictionary to hold loaded sounds
        self.sounds = {}

        # Load sounds into memory

        # tower sounds
        self.load_sound("base_shoot", "steam_shoot.wav")
        self.load_sound("aoe_shoot", "aoe_thud.wav")
        self.load_sound("laser_shoot", "laser_hum.wav")
        self.load_sound("build", "build_clang.wav")

        # UI sounds
        self.load_sound("easter_egg", "easter_egg.wav")
        self.load_sound("ui_menu", "ui_menu.wav")
        self.load_sound("ui_close", "ui_menu_close.wav")
        self.load_sound("ui_select", "ui_click.wav")
        self.load_sound("ui_error", "ui_error.wav")

        # Time Control Sounds
        self.load_sound("ui_pause", "ui_pause.wav")
        self.load_sound("ui_unpause", "ui_unpause.wav")
        self.load_sound("ui_speed_up", "ui_speed_up.wav")
        self.load_sound("ui_slow_down", "ui_slow_down.wav")

        # Ambiance Sounds
        self.load_sound("bg_ambiance", "ambience_loop.wav")


        # Volume settings
        self.master_volume = 0.5
        self.music_player = None

    def load_sound(self, key, filename):
        """Safely loads a sound file."""
        path = SOUND_DIR / filename
        if path.exists():
            self.sounds[key] = arcade.load_sound(path)
        else:
            print(f"Warning: Sound file not found: {filename}")

    def play_sound(self, key, volume=1.0):
        """Plays a sound by key."""
        if key in self.sounds:
            # Arcade's play_sound returns a player object, which we can ignore for now
            arcade.play_sound(self.sounds[key], volume * self.master_volume)

    def start_ambience(self):
        """Starts the background loop."""
        if "bg_ambiance" in self.sounds and self.music_player is None:
            # loop=True makes it repeat forever
            # volume=0.3 keeps it subtle so SFX pop over it
            self.music_player = arcade.play_sound(
                self.sounds["bg_ambiance"],
                volume=0.3 * self.master_volume,
                loop=True
            )

    def stop_ambience(self):
        """Stops the background loop (e.g., on Game Over)."""
        if self.music_player:
            arcade.stop_sound(self.music_player)
            self.music_player = None