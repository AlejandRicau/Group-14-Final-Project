import arcade
import sys
import os
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.views.start_view import StartView


def main():
    """ Main entry point for the game """

    # --- PYINSTALLER SETUP ---
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    # -------------------------

    # 1. Create the Window FIRST
    # We do not pass tile_size/grid here, just pixel dimensions
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Steam Tunnels Defense")

    # 2. Center it
    window.center_window()

    # 3. Create the View
    # The View's __init__ will call arcade.get_window(), which now works
    # because 'window' exists!
    start_view = StartView()

    # 4. Show the View
    window.show_view(start_view)

    # 5. Run
    arcade.run()


if __name__ == "__main__":
    main()