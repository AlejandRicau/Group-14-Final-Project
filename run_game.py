import os
import sys
import ctypes

# --- WINDOWS DPI FIX ---
if os.name == 'nt':
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass
# -----------------------

# We import arcade inside the try block or main to be safe,
# but usually the crash happens at Window creation.
import arcade
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from src.views.start_view import StartView


def main():
    """ Main entry point for the game """

    # PyInstaller Setup
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    try:
        # 1. Try to create the Window
        window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Steam Tunnels Defense")
        window.center_window()

        # 2. Show Start View
        start_view = StartView()
        window.show_view(start_view)

        # 3. Run
        arcade.run()

    except Exception as e:
        # Check if it's an OpenGL error
        error_str = str(e)
        if "OpenGL" in error_str or "glCreateShader" in error_str:
            print("\n" + "=" * 60)
            print("CRITICAL GRAPHICS ERROR")
            print("=" * 60)
            print("Your computer's graphics drivers are missing or too old.")
            print("This game requires OpenGL 3.3+.")
            print(f"Details: {e}")
            print("=" * 60 + "\n")

            # Optional: Show a native Windows popup so they see it even if console closes
            if os.name == 'nt':
                ctypes.windll.user32.MessageBoxW(0,
                                                 f"Graphics Error: Your GPU drivers do not support OpenGL 3.3.\n\nPlease update your Intel/NVIDIA/AMD drivers.",
                                                 "Steam Tunnels Defense - Error", 0x10)
        else:
            # Some other crash
            raise e


if __name__ == "__main__":
    main()