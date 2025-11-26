from constants import *
from random import uniform
import arcade

class LaserEffect:
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.total_time = LASER_VISUAL_EFFECT_DURATION
        self.time_left = LASER_VISUAL_EFFECT_DURATION

    def update(self, delta_time):
        self.time_left -= delta_time
        if self.time_left < 0:
            self.time_left = 0

    def draw(self):
        if self.time_left <= 0:
            return

        '''beam characteristics'''
        progress = self.time_left / self.total_time
        alpha_of_t = int(255 * progress)

        # beam colors
        color_core = (255, 255, 255, alpha_of_t)
        color_outer = (200, 200, 200, alpha_of_t // 2)

        # beam width
        core_width = 3 * progress + 1  # starts 4px → shrinks to 1px
        outer_width = 8 * progress + 2  # starts 10px → shrinks to 2px

        # introduce wobbling effect
        wobbling = uniform(-1.5, 1.5)
        end_pos_x = self.end_x + wobbling
        end_pos_y = self.end_y + wobbling

        '''Draw the visual effect'''
        draw_line_with_gradient(       # core line
            self.start_x, self.start_y,
            end_pos_x, end_pos_y,
            color_core, core_width, 12)

        draw_line_with_gradient(       # outer line
            self.start_x, self.start_y,
            end_pos_x, end_pos_y,
            color_outer, outer_width, 12)

        arcade.draw_circle_filled(      # pressure ring at the tower
            self.start_x, self.start_y,
            10 * progress ** 2,
            (255, 255, 255, alpha_of_t)
        )

        arcade.draw_circle_filled(      # pressure ring at the end of beam3
            self.end_x, self.end_y,
            3 * progress ** 2,
            (200, 200, 200, alpha_of_t)
        )



def draw_line_with_gradient(
        start_x, start_y, end_x, end_y,
        color, width, step):
    """
    Draw a line with a gradient of alpha

    Args:
        start_x (int): Start x position
        start_y (int): Start y position
        end_x (int): End x position
        end_y (int): End y position
        color (tuple): Color of the line
        width (float): Width of the line
        step (int): Number of steps/segments to draw the line
    """
    # draw the line with gradient segment by segment
    for i in range(step):
        # t0 = start of segment, t1 = end of segment (0 → 1)
        t0 = i / step
        t1 = (i + 1) / step

        # Interpolate segment endpoints
        x0 = start_x + (end_x - start_x) * t0
        y0 = start_y + (end_y - start_y) * t0
        x1 = start_x + (end_x - start_x) * t1
        y1 = start_y + (end_y - start_y) * t1

        alpha_of_x = int(color[3] * (1.0 - i / step))     # alpha of each segment
        color_of_x = (color[0], color[1], color[2], alpha_of_x)    # color of each segment

        arcade.draw_line(x0, y0, x1, y1, color_of_x, width)

