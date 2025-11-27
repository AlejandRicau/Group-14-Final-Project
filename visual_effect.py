from constants import *
from random import uniform
import arcade
import math

class LaserEffect:
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__()
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.total_time = 1.5
        self.time_left = 1.5
        self.can_be_removed = False

    def update(self, delta_time):
        self.time_left -= delta_time
        if self.time_left < 0:
            self.time_left = 0

        if self.time_left <= 0:
            self.can_be_removed = True

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
            (200, 200, 200, alpha_of_t))



class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y):
        # initialize bullet properties
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = BULLET_SPEED

        # Compute normalized direction
        self.dir_x, self.dir_y = unit_direction_vector(start_x, start_y, target_x, target_y)

        # initialize bullet state
        self.can_be_removed = False
        self.trail_length = 10  # pixels
        self.time_alive = 0.0

    def update(self, delta_time):
        if self.can_be_removed:
            return

        # move the bullet as per its direction
        move_dist = self.speed * delta_time
        self.current_x += self.dir_x * move_dist
        self.current_y += self.dir_y * move_dist
        self.time_alive += delta_time

        # Check if reached target
        distance_traveled = math.hypot(self.current_x - self.start_x, self.current_y - self.start_y)
        distance_total    = math.hypot(self.target_x  - self.start_x, self.target_y  - self.start_y)
        if distance_traveled >= distance_total:
            self.can_be_removed = True

    def draw(self):
        if self.can_be_removed:
            return
        alpha = max(0, 255 - int(self.time_alive * 1000))  # fade over time
        arcade.draw_line(
            self.current_x - self.dir_x * self.trail_length,
            self.current_y - self.dir_y * self.trail_length,
            self.current_x,
            self.current_y,
            (255, 255, 255, alpha),
            2)



class SteamBoom:
    def __init__(self, tower, visual_effect_list):
        # initialize steam boom properties
        self.tower = tower
        self.start_x = tower.center_x
        self.start_y = tower.center_y
        self.current_x = tower.center_x
        self.current_y = tower.center_y
        self.target_x = tower.on_target.center_x
        self.target_y = tower.on_target.center_y
        self.speed = BOOM_SPEED
        self.visual_effect_list = visual_effect_list

        # Initialize normalized direction
        self.dir_x, self.dir_y = 1, 1

        # initialize bullet state
        self.can_be_removed = False
        self.trail = []  # Keep past positions for a trailing effect
        self.trail_length = 10  # number of segments in the trail

    def update(self, delta_time):
        if self.can_be_removed:
            return

        # Move projectile based on adjusting direction for correct aiming
        self.dir_x, self.dir_y = unit_direction_vector(
            self.current_x, self.current_y, self.target_x, self.target_y)
        self.current_x += self.dir_x * self.speed * delta_time
        self.current_y += self.dir_y * self.speed * delta_time

        # Add to trail
        self.trail.append((self.current_x, self.current_y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        # Check if reached target
        distance_to_target = math.hypot(self.target_x - self.start_x, self.target_y - self.start_y)
        distance_traveled = math.hypot(self.current_x - self.start_x, self.current_y - self.start_y)
        if distance_traveled >= distance_to_target:
            # Spawn the puff effect at target
            self.visual_effect_list.append(
                SteamPuff(self.target_x, self.target_y, size=EXPLODE_PUFF_SIZE_AOE)
            )
            # deal the damage
            for enemy in self.tower.damage_enemy_list:
                enemy.deal_damage(self.tower.damage)
            self.can_be_removed = True

    def draw(self):
        # Draw trail
        for i, (x, y) in enumerate(self.trail):
            # older positions are drawn smaller and more transparent,
            # newer positions are brighter and larger.
            alpha = int(255 * (i + 1) / len(self.trail))
            radius = 4 * (i + 1) / len(self.trail)
            arcade.draw_circle_filled(x, y, radius, (200, 200, 255, alpha))

        # Draw the “head” of the projectile
        if not self.can_be_removed:
            arcade.draw_circle_filled(self.current_x, self.current_y, 5, (255, 255, 255))



class SteamPuff:
    def __init__(self, x, y, size, delay=0):
        self.x = x
        self.y = y
        self.size = size
        self.alpha = 200
        self.time_left = 0.3
        self.time_delay = delay
        self.can_be_removed = False

    def update(self, dt):
        if self.time_delay > 0:     # updating through the delay time
            self.time_delay -= dt
            return

        self.time_left -= dt
        self.size += 40 * dt  # grows quickly
        self.alpha = int(200 * (self.time_left / 0.3))

        if self.time_left <= 0:
            self.can_be_removed = True

    def draw(self):
        if self.time_delay > 0:     # delay before drawing
            return

        if self.time_left > 0:
            arcade.draw_circle_filled(
                self.x, self.y, self.size,
                (255, 255, 255, self.alpha))



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

def unit_direction_vector(x_start, y_start, x_target, y_target):
    """
    Calculate the unit direction vector from start to target
    """
    dx = x_target - x_start
    dy = y_target - y_start
    distance = math.hypot(dx, dy)
    return dx / distance, dy / distance