from constants import *
from Map import Map
import arcade


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.tile_size = tile_size
        self.map = Map(width, height)
        self.camera = arcade.camera.Camera2D()

        self.sprite_list = arcade.SpriteList()
        for row in self.map.map:  # map.map is your 2D tile matrix
            for tile in row:
                self.sprite_list.append(tile)

        # camera control parameters
        self.camera_speed = 20
        self.keys_held = set()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.sprite_list.draw()             # draw all sprites

    def on_update(self, delta_time: float):
        # smooth camera movement
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
            self.rebuild_sprite_list()

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0]
            )
            self.rebuild_sprite_list()

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6, add_new_spawns_goals=False)
            self.rebuild_sprite_list()

        elif symbol == arcade.key.F:
            self.map.generate_new_special_point("spawn")
            self.rebuild_sprite_list()

        elif symbol == arcade.key.G:
            self.map.generate_new_special_point("goal")
            self.rebuild_sprite_list()

        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_held:
            self.keys_held.remove(symbol)

    def rebuild_sprite_list(self):
        """Rebuilds the sprite list from the map"""
        self.sprite_list.clear()
        for row in self.map.map:
            for tile in row:
                tile.update_texture()  # ensure the texture matches the state
                self.sprite_list.append(tile)



def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()