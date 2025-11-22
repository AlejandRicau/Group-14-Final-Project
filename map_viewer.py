from constants import *
from helper_functions import *
from Map import Map
import arcade
from Tower import BaseTower


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.tile_size = tile_size
        self.map = Map(width, height)
        self.camera = arcade.camera.Camera2D()
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        self.background_list = arcade.SpriteList()
        for row in self.map.map:  # map.map is your 2D tile matrix
            for tile in row:
                self.background_list.append(tile)

        self.tower_list = arcade.SpriteList()

        # camera control parameters
        self.camera_speed = 20
        self.keys_held = set()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.background_list.draw()
        self.tower_list.draw()

    def on_update(self, delta_time: float):
        """Updates the camera position based on the keys held."""

        '''Smooth camera movement'''
        dx = dy = 0
        if arcade.key.LEFT in self.keys_held:
            dx -= self.camera_speed
        if arcade.key.RIGHT in self.keys_held:
            dx += self.camera_speed
        if arcade.key.UP in self.keys_held:
            dy += self.camera_speed
        if arcade.key.DOWN in self.keys_held:
            dy -= self.camera_speed

        if dx != 0 or dy != 0:
            x, y = self.camera.position
            self.camera.position = (x + dx, y + dy)

    def on_key_press(self, symbol, modifiers):
        self.keys_held.add(symbol)

        if symbol == arcade.key.M:
            self.map.generate_new_map()
            self.rebuild_background_list()
            self.tower_list.clear()

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0]
            )
            self.rebuild_background_list()

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6, add_new_spawns_goals=False)
            self.rebuild_background_list()

        elif symbol == arcade.key.F:
            self.map.generate_new_special_point("spawn")
            self.rebuild_background_list()

        elif symbol == arcade.key.G:
            self.map.generate_new_special_point("goal")
            self.rebuild_background_list()

        elif symbol == arcade.key.T:
            self.keys_held.add(symbol)

        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_held:
            self.keys_held.remove(symbol)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.add_tower(x, y)

    def rebuild_background_list(self):
        """Rebuilds the sprite list from the map"""
        self.background_list.clear()
        for row in self.map.map:
            for tile in row:
                tile.update_texture()  # ensure the texture matches the state
                self.background_list.append(tile)

    def add_tower(self, mouse_x, mouse_y):
        """
        Adds a tower to the map at the tile hovered by the mouse if T is held.

        Args:
            mouse_x (int): The x-coordinate of the mouse
            mouse_y (int): The y-coordinate of the mouse
        """
        # convert mouse position to tile position and find the tile_curr
        world_x, world_y, _ = self.camera.unproject((mouse_x, mouse_y, 0))
        tx, ty = pixel_to_tile(world_x, world_y, self.tile_size)
        tile_hovered = self.map.map[ty][tx]
        print(tile_hovered)

        # check validity
        if not self.is_valid_tower_location(tile_hovered):
            return

        # check if T is held
        if arcade.key.T not in self.keys_held:
            return

        # add tower
        tower = BaseTower(tile_hovered)
        self.tower_list.append(tower)

    def is_valid_tower_location(self, tile):
        """
        Returns True if the tile is a valid location for a tower.

        Args:
            tile (Tile): The tile to check

        Returns:
            bool: True if the tile is a valid location for a tower, False otherwise
        """
        # initialize the bool value
        valid = False

        # check if the tile is next to a path
        surrounding_tiles = self.map.get_surrounding_tiles(tile)
        for idx, t in enumerate(surrounding_tiles):
            if idx == len(surrounding_tiles) // 2:      # the tile hovered
                if t.get_state() != 'empty':        # the tile hovered cannot be  empty
                    return False
            if t.get_state() == 'path':     # the tile hovered cannot be next to a path
                valid = True
        return valid


def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()