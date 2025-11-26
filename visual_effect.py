from constants import *
import arcade

class LaserEffect(arcade.Sprite):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.duration = LASER_VISUAL_EFFECT_DURATION
        self.elapsed = 0
        self.color: tuple[int, int, int] = arcade.color.RED
        self.width = 3

    def visual_update(self, delta_time):
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.kill()  # remove from sprite list

    def draw(self):
        arcade.draw_line(
            self.start_x,
            self.start_y,
            self.end_x,
            self.end_y,
            self.color,
            self.width
        )
