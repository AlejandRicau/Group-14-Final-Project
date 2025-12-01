from src.constants import *
from random import uniform
import arcade
import math
from arcade.experimental.shadertoy import Shadertoy
from pathlib import Path

# ==========================================
#        DYNAMIC PATH CONFIGURATION
# ==========================================
# 1. Get the directory of THIS file (src/utils/)
CURRENT_FILE_DIR = Path(__file__).parent

# 2. Go up 2 levels to the Project Root (src/utils -> src -> root)
PROJECT_ROOT = CURRENT_FILE_DIR.parent.parent

# 3. Define the Shaders folder
# IMPORTANT: Check if your folder is named "shaders" or "Shaders" (Case Sensitive!)
SHADER_DIR = PROJECT_ROOT / "assets" / "shaders"
# ==========================================

def get_robust_pixel_ratio(window):
    """
    Calculates the true pixel ratio by comparing Framebuffer to Window size.
    Fixes issues where get_pixel_ratio() returns 1.0 on High-DPI screens.
    """
    width, height = window.get_size()
    fb_width, fb_height = window.get_framebuffer_size()
    if width == 0: return 1.0 # Safety
    return fb_width / width


class OrbShader:
    """Handles glowing circles (AOE, Goals)"""

    def __init__(self, window_size):
        shader_path = SHADER_DIR / "glow_point.glsl"
        self.shader = Shadertoy.create_from_file(window_size, str(shader_path))

    def render(self, object_list, camera, color=(1.0, 0.1, 0.1)):
        if not object_list: return

        window = arcade.get_window()
        pixel_ratio = get_robust_pixel_ratio(window)

        flat_data = []
        for p in object_list:
            # --- FIX: Handle different position attributes ---
            if hasattr(p, 'current_x'):
                wx, wy = p.current_x, p.current_y
            elif hasattr(p, 'center_x'):
                wx, wy = p.center_x, p.center_y
            else:
                continue

            pos = camera.project((wx, wy))
            if not pos: continue

            flat_data.append(pos[0] * pixel_ratio)
            flat_data.append(pos[1] * pixel_ratio)

        if not flat_data: return

        # Pad to 100 points
        count = len(flat_data) // 2
        if count > 100:
            flat_data = flat_data[:200]
            count = 100
        else:
            flat_data.extend([0.0] * (200 - len(flat_data)))

        self.shader.program['u_point_count'] = count
        self.shader.program['u_points'] = flat_data
        self.shader.program['u_color'] = color
        self.shader.render()


class BeamShader:
    """Handles SOLID glowing lines (Bullets)"""

    def __init__(self, window_size):
        shader_path = SHADER_DIR / "glow_beam.glsl"
        self.shader = Shadertoy.create_from_file(window_size, str(shader_path))

    def render(self, bullet_list, camera, color=(1.0, 0.9, 0.5)):
        if not bullet_list: return

        window = arcade.get_window()
        pixel_ratio = get_robust_pixel_ratio(window)

        flat_data = []
        for b in bullet_list:
            if not isinstance(b, Bullet): continue

            # --- Bullet Logic (World -> Screen) ---
            head_world = (b.current_x, b.current_y)
            beam_len = b.trail_length * 1.5
            tail_world_x = b.current_x - (b.dir_x * beam_len)
            tail_world_y = b.current_y - (b.dir_y * beam_len)

            head_screen = camera.project(head_world)
            tail_screen = camera.project((tail_world_x, tail_world_y))

            if not head_screen or not tail_screen: continue

            flat_data.append(head_screen[0] * pixel_ratio)
            flat_data.append(head_screen[1] * pixel_ratio)
            flat_data.append(tail_screen[0] * pixel_ratio)
            flat_data.append(tail_screen[1] * pixel_ratio)

        if not flat_data: return
        self._send_to_gpu(flat_data, color)

    def _send_to_gpu(self, flat_data, color):
        # Helper to avoid code duplication
        count = len(flat_data) // 4
        if count > 100:
            flat_data = flat_data[:400]
            count = 100
        else:
            flat_data.extend([0.0] * (400 - len(flat_data)))

        self.shader.program['u_line_count'] = count
        self.shader.program['u_lines'] = flat_data
        self.shader.program['u_color'] = color
        self.shader.render()


class LaserShader:
    """Handles GRADIENT glowing lines (Lasers)"""

    def __init__(self, window_size):
        shader_path = SHADER_DIR / "glow_laser.glsl"
        self.shader = Shadertoy.create_from_file(window_size, str(shader_path))

    def render(self, laser_list, camera, color=(0.4, 1.0, 0.6)):
        if not laser_list: return

        window = arcade.get_window()
        pixel_ratio = get_robust_pixel_ratio(window)

        flat_data = []
        for l in laser_list:
            if not isinstance(l, LaserEffect): continue

            # --- Laser Logic (Explicit Start/End) ---
            # IMPORTANT: For gradient to work, Start must be Tower, End must be Target
            start_screen = camera.project((l.start_x, l.start_y))
            end_screen = camera.project((l.end_x, l.end_y))

            if not start_screen or not end_screen: continue

            flat_data.append(start_screen[0] * pixel_ratio)
            flat_data.append(start_screen[1] * pixel_ratio)
            flat_data.append(end_screen[0] * pixel_ratio)
            flat_data.append(end_screen[1] * pixel_ratio)

        if not flat_data: return

        # Reuse same padding logic
        count = len(flat_data) // 4
        if count > 100:
            flat_data = flat_data[:400]
            count = 100
        else:
            flat_data.extend([0.0] * (400 - len(flat_data)))

        self.shader.program['u_line_count'] = count
        self.shader.program['u_lines'] = flat_data
        self.shader.program['u_color'] = color
        self.shader.render()


class SteamShader:
    def __init__(self, window_size):
        shader_path = SHADER_DIR / "steam.glsl"
        self.shader = Shadertoy.create_from_file(window_size, str(shader_path))

    def render(self, puff_list, camera):
        if not puff_list: return

        window = arcade.get_window()
        pixel_ratio = get_robust_pixel_ratio(window)

        # Flat list of 3 floats per puff: [x, y, radius]
        flat_data = []

        for p in puff_list:
            if not isinstance(p, SteamPuff): continue

            # Project Position
            screen_pos = camera.project((p.x, p.y))
            if not screen_pos: continue

            px = screen_pos[0] * pixel_ratio
            py = screen_pos[1] * pixel_ratio

            # Scale Radius based on pixel ratio
            pr = p.size * pixel_ratio

            flat_data.append(float(px))
            flat_data.append(float(py))
            flat_data.append(float(pr))

        if not flat_data: return

        # 100 Puffs * 3 floats = 300 floats total
        MAX_PUFFS = 100
        REQUIRED_FLOATS = MAX_PUFFS * 3
        count = len(flat_data) // 3

        if len(flat_data) > REQUIRED_FLOATS:
            flat_data = flat_data[:REQUIRED_FLOATS]
            count = MAX_PUFFS
        elif len(flat_data) < REQUIRED_FLOATS:
            flat_data.extend([0.0] * (REQUIRED_FLOATS - len(flat_data)))

        try:
            self.shader.program['u_puff_count'] = count
            self.shader.program['u_puffs'] = flat_data
            self.shader.render()
        except Exception as e:
            print(f"Steam Error: {e}")


class VignetteShader:
    def __init__(self, window_size):
        shader_path = SHADER_DIR / "vignette.glsl"
        self.shader = Shadertoy.create_from_file(window_size, str(shader_path))

    def render(self, tower_list, camera):
        # We render even if tower_list is empty, because we still need the base vignette!

        window = arcade.get_window()
        pixel_ratio = get_robust_pixel_ratio(window)

        flat_data = []

        if tower_list:
            for t in tower_list:
                # Project Tower World Pos -> Screen Pixels
                pos = camera.project((t.center_x, t.center_y))
                if pos:
                    flat_data.append(pos[0] * pixel_ratio)
                    flat_data.append(pos[1] * pixel_ratio)

        # Pad to 100 points (200 floats)
        # Note: If list is empty, this creates a list of 200 zeros, which is fine.
        count = len(flat_data) // 2

        if count > 100:
            flat_data = flat_data[:200]
            count = 100
        else:
            flat_data.extend([0.0] * (200 - len(flat_data)))

        self.shader.program['u_tower_count'] = count
        self.shader.program['u_towers'] = flat_data

        # Render the darkness
        self.shader.render()

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
    def __init__(self, start_x, start_y, target_x, target_y, visual_effect_list, target_enemy, damage):
        self.visual_effect_list = visual_effect_list

        # Store game logic data
        self.target_enemy = target_enemy
        self.damage = damage

        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = BULLET_SPEED

        self.dir_x, self.dir_y = unit_direction_vector(start_x, start_y, target_x, target_y)

        self.can_be_removed = False
        self.trail_length = 10
        self.time_alive = 0.0

    def update(self, delta_time):
        if self.can_be_removed:
            return

        move_dist = self.speed * delta_time
        self.current_x += self.dir_x * move_dist
        self.current_y += self.dir_y * move_dist
        self.time_alive += delta_time

        # Check Arrival
        distance_traveled = math.hypot(self.current_x - self.start_x, self.current_y - self.start_y)
        distance_total = math.hypot(self.target_x - self.start_x, self.target_y - self.start_y)

        if distance_traveled >= distance_total:
            # --- FIX: Deal Damage HERE (Synced with Visuals) ---
            # We check if the enemy is still alive/valid before hitting them
            if self.target_enemy and self.target_enemy.health > 0:
                self.target_enemy.deal_damage(self.damage)

            # Spawn Puff
            self.visual_effect_list.append(
                SteamPuff(
                    self.target_x,
                    self.target_y,
                    size=EXPLODE_PUFF_SIZE_BASIC
                )
            )
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



class CooldownEffect:
    def __init__(self, tower):
        """
        Visual overlay showing tower cooldown.

        Args:
            tower: the tower this overlay belongs to
        """
        self.tower = tower
        self.max_alpha = COOLDOWN_OPACITY_LIMIT
        self.alpha = 0

    def update(self):
        """
        Update overlay alpha based on tower cooldown.
        """
        # cooldown goes from full -> 0
        full_cd = 1.0 / self.tower.frequency
        cd = self.tower.cooldown

        if cd > 0:
            ratio = cd / full_cd       # 1 → 0
            self.alpha = int(self.max_alpha * ratio)
        else:
            self.alpha = 0

    def draw(self):
        """
        Draw overlay above the tower.
        """
        if self.alpha <= 0:
            return

        # Draw a thick vertical line as cooldown overlay
        arcade.draw_line(
            self.tower.center_x,  # start_x
            self.tower.center_y - TOWER_SIZE[1] / 2,  # start_y (bottom of tower)
            self.tower.center_x,  # end_x
            self.tower.center_y + TOWER_SIZE[1] / 2,  # end_y (top of tower)
            (0, 0, 0, self.alpha),  # color with alpha
            line_width=TOWER_SIZE[0]  # make the line as wide as the tower
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

def unit_direction_vector(x_start, y_start, x_target, y_target):
    """
    Calculate the unit direction vector from start to target
    """
    dx = x_target - x_start
    dy = y_target - y_start
    distance = math.hypot(dx, dy)
    return dx / distance, dy / distance