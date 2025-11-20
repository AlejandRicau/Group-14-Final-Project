from constants import *
from Map import Map
import arcade
from PIL import Image, ImageDraw


class MapViewer(arcade.Window):
    def __init__(self, width, height, tile_size):
        super().__init__(width * tile_size, height * tile_size, "Map Visualizer")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # Tile grid properties
        self.tile_size = tile_size
        self.map = Map(width, height)
        self.grid_width = width
        self.grid_height = height
        self.pixel_width = width * tile_size
        self.pixel_height = height * tile_size

        self.camera = arcade.camera.Camera2D()

        # Scene and map sprite
        self.scene = arcade.Scene()
        self.map_sprite = None
        self.create_map_sprite()  # Create the map sprite

        # camera control parameters
        self.camera_speed = 20
        self.keys_held = set()

    def on_draw(self):
        self.clear()
        self.camera.use()

        # Just draw the scene - the map sprite is already in there!
        self.scene.draw()

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
            self.update_map_sprite()  # Update the sprite!

        elif symbol == arcade.key.P:
            self.map.recursive_path_generation(
                self.map.spawns[0],
                self.map.goals[0],
                detour_chance=0.4
            )
            self.update_map_sprite()  # Update the sprite!

        elif symbol == arcade.key.E:
            self.map.expand_map(add_width=6, add_height=6, add_new_spawns_goals=False)
            self.update_map_sprite()  # Update the sprite!

        elif symbol == arcade.key.F:
            self.map.generate_new_special_point("spawn")
            self.update_map_sprite()  # Update the sprite!

        elif symbol == arcade.key.G:
            self.map.generate_new_special_point("goal")
            self.update_map_sprite()  # Update the sprite!

        elif symbol == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol in self.keys_held:
            self.keys_held.remove(symbol)

    def update_map_sprite(self):
        """Update the map sprite when the map data changes"""
        # Remove old sprite from scene
        if self.map_sprite:
            self.map_sprite.remove_from_sprite_lists()

        # Create new sprite with updated map
        self.create_map_sprite()

    def create_map_sprite(self):
        """Create a single sprite that contains the entire map grid"""

        texture_width = self.map.width * self.tile_size
        texture_height = self.map.height * self.tile_size

        # Create a blank PIL image
        img = Image.new("RGBA", (texture_width, texture_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw each tile onto the PIL image
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
                elif cell.color == 4:
                    color = COLOR_BORDER
                else:
                    color = arcade.color.BLACK

                # Convert Arcade RGB tuple → PIL RGBA
                rgba = (*color, 255)

                # Draw pixel rect
                left = x * self.tile_size
                top = y * self.tile_size
                right = left + self.tile_size - 1
                bottom = top + self.tile_size - 1

                draw.rectangle([left, top, right, bottom], fill=color)

        # Convert PIL image → Arcade texture
        texture = arcade.Texture("map_texture", img)

        # Create sprite
        self.map_sprite = arcade.Sprite(
            texture=texture,
            center_x=texture_width // 2,
            center_y=texture_height // 2
        )

        # Add to scene
        self.scene.add_sprite("Map", self.map_sprite)


def main():
    grid_width = SCREEN_WIDTH // TILE_SIZE
    grid_height = SCREEN_HEIGHT // TILE_SIZE
    window = MapViewer(grid_width, grid_height, TILE_SIZE)
    arcade.run()


if __name__ == "__main__":
    main()