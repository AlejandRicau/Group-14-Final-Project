from constants import *
from Map import Map


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.tile_size = tile_size
        self.map = Map(width, height)

    def on_draw(self):
        self.clear()
        for y in range(self.map.height):
            for x in range(self.map.width):
                cell = self.map.map[y][x]
                if cell.color == 0:
                    color = COLOR_EMPTY
                elif cell.color == 1:
                    color = COLOR_PATH
                elif cell.color == 2:
                    color = COLOR_SPAWN
                elif cell.color == 3:
                    color = COLOR_GOAL
                else:
                    color = arcade.color.BLACK

                rect = arcade.rect.LBWH(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size - 1,
                    self.tile_size - 1
                )
                arcade.draw_rect_filled(rect, color)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.M:  # regenerate map (new spawn & goal)
            self.map.generate_new_map()
        elif symbol == arcade.key.P:  # regenerate path (same spawn & goal)
            self.map.recursive_path_generation(self.map.spawn[0], self.map.goal[0], detour_chance=0.4)
        elif symbol == arcade.key.ESCAPE:
            self.close()


def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()
