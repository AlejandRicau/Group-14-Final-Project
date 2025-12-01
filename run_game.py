import os
import sys

# --- WINDOWS DPI FIX (Keep this for your teammate!) ---
if os.name == 'nt':
    import ctypes

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass
# ----------------------------------------------------

import arcade
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from src.views.start_view import StartView


def main():
    """ Main entry point for the game """

    # --- PYINSTALLER SETUP ---
    # Ensures assets are found when bundled as an exe/app
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    # -------------------------

    # 1. CREATE THE WINDOW FIRST
    # We must create the window before any Views can be initialized.
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Steam Tunnels Defense")
    window.center_window()

    # 2. CREATE THE START VIEW
    # Now that the window exists, we can create views.
    start_view = StartView()

    # 3. SHOW THE VIEW
    window.show_view(start_view)

    # 4. RUN
    arcade.run()


if __name__ == "__main__":
    main()