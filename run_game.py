import arcade
from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.views.start_view import StartView  # <--- Changed


def main():
    """ Main entry point for the game """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "UT Steam Tunnels Defense")
    window.center_window()

    # Show the Start View
    start_view = StartView()
    window.show_view(start_view)

    arcade.run()


if __name__ == "__main__":
    main()