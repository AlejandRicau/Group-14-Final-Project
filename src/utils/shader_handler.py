import arcade
from pathlib import Path
from arcade.experimental.shadertoy import Shadertoy
from src.utils.visual_effect import Bullet, LaserEffect, SteamPuff, SteamBoom

# --- DYNAMIC PATH SETUP ---
CURRENT_FILE_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_FILE_DIR.parent.parent
SHADER_DIR = PROJECT_ROOT / "assets" / "shaders"


class BaseShader:
    def __init__(self, window_size, shader_filename):
        path = SHADER_DIR / shader_filename
        self.available = False
        self.shader = None

        try:
            # Attempt to compile the shader on the GPU
            self.shader = Shadertoy.create_from_file(window_size, str(path))
            self.available = True
        except Exception as e:
            # If it fails (No GPU, driver issue, etc.), we log it and continue safely
            print(f"[System] Warning: Failed to load shader '{shader_filename}'. Effects disabled.")
            print(f"Reason: {e}")
            self.available = False

    def _get_pixel_ratios(self):
        if not self.available: return 1.0, 1.0

        window = arcade.get_window()
        width, height = window.get_size()
        fb_width, fb_height = window.get_framebuffer_size()

        if width == 0 or height == 0: return 1.0, 1.0

        scale_x = fb_width / width
        scale_y = fb_height / height
        return scale_x, scale_y

    def _project_and_scale(self, camera, wx, wy, scale_x, scale_y):
        screen_pos = camera.project((wx, wy))
        if screen_pos is not None:
            return screen_pos[0] * scale_x, screen_pos[1] * scale_y

        cam_x = camera.position.x
        cam_y = camera.position.y
        return (wx - cam_x) * scale_x, (wy - cam_y) * scale_y

    def _send_to_gpu(self, flat_data, count_uniform, list_uniform, max_points, items_per_point, color=None, shape=None):
        if not self.available: return  # Double check

        count = len(flat_data) // items_per_point

        if count > max_points:
            flat_data = flat_data[:max_points * items_per_point]
            count = max_points
        else:
            needed = (max_points * items_per_point) - len(flat_data)
            flat_data.extend([0.0] * needed)

        try:
            self.shader.program[count_uniform] = count
            self.shader.program[list_uniform] = flat_data
            if color:
                self.shader.program['u_color'] = color
            if shape is not None:
                self.shader.program['u_shape'] = shape
            self.shader.render()
        except Exception as e:
            # If rendering fails mid-game, disable this shader to prevent stuttering/crashes
            print(f"Shader Runtime Error: {e}")
            self.available = False


class OrbShader(BaseShader):
    """Handles glowing circles (AOE, Goals)."""

    def __init__(self, window_size):
        super().__init__(window_size, "glow_point.glsl")

    def render(self, object_list, camera, color=(1.0, 0.1, 0.1)):
        # --- PROTECTION CHECK ---
        if not self.available or not object_list: return

        sx, sy = self._get_pixel_ratios()
        flat_data = []
        for p in object_list:
            if hasattr(p, 'current_x'):
                wx, wy = p.current_x, p.current_y
            elif hasattr(p, 'center_x'):
                wx, wy = p.center_x, p.center_y
            else:
                continue

            px, py = self._project_and_scale(camera, wx, wy, sx, sy)
            flat_data.append(px);
            flat_data.append(py)

        self._send_to_gpu(flat_data, 'u_point_count', 'u_points', 100, 2, color)


class BeamShader(BaseShader):
    """Handles SOLID glowing lines (Bullets)."""

    def __init__(self, window_size):
        super().__init__(window_size, "glow_beam.glsl")

    def render(self, bullet_list, camera, color=(1.0, 0.9, 0.5)):
        if not self.available or not bullet_list: return

        sx, sy = self._get_pixel_ratios()
        flat_data = []
        for b in bullet_list:
            if not isinstance(b, Bullet): continue

            head_wx, head_wy = b.current_x, b.current_y
            beam_len = b.trail_length * 1.5
            tail_wx = head_wx - (b.dir_x * beam_len)
            tail_wy = head_wy - (b.dir_y * beam_len)

            hx, hy = self._project_and_scale(camera, head_wx, head_wy, sx, sy)
            tx, ty = self._project_and_scale(camera, tail_wx, tail_wy, sx, sy)

            flat_data.extend([hx, hy, tx, ty])

        self._send_to_gpu(flat_data, 'u_line_count', 'u_lines', 100, 4, color)


class LaserShader(BaseShader):
    """Handles GRADIENT glowing lines (Lasers)."""

    def __init__(self, window_size):
        super().__init__(window_size, "glow_laser.glsl")

    def render(self, laser_list, camera, color=(0.4, 1.0, 0.6)):
        if not self.available or not laser_list: return

        sx, sy = self._get_pixel_ratios()
        flat_data = []
        for l in laser_list:
            if not isinstance(l, LaserEffect): continue

            start_x, start_y = self._project_and_scale(camera, l.start_x, l.start_y, sx, sy)
            end_x, end_y = self._project_and_scale(camera, l.end_x, l.end_y, sx, sy)

            flat_data.extend([start_x, start_y, end_x, end_y])

        self._send_to_gpu(flat_data, 'u_line_count', 'u_lines', 100, 4, color)


class SteamShader(BaseShader):
    """Handles soft clouds."""

    def __init__(self, window_size):
        super().__init__(window_size, "steam.glsl")

    def render(self, puff_list, camera):
        if not self.available or not puff_list: return

        sx, sy = self._get_pixel_ratios()
        flat_data = []
        for p in puff_list:
            if not isinstance(p, SteamPuff): continue

            px, py = self._project_and_scale(camera, p.x, p.y, sx, sy)
            pr = p.size * ((sx + sy) / 2)

            flat_data.extend([px, py, pr])

        self._send_to_gpu(flat_data, 'u_puff_count', 'u_puffs', 100, 3)


class VignetteShader(BaseShader):
    """Handles Fog of War."""

    def __init__(self, window_size):
        super().__init__(window_size, "vignette.glsl")

    def render(self, tower_list, camera):
        if not self.available: return

        sx, sy = self._get_pixel_ratios()
        flat_data = []
        if tower_list:
            for t in tower_list:
                px, py = self._project_and_scale(camera, t.center_x, t.center_y, sx, sy)
                flat_data.extend([px, py])

        self._send_to_gpu(flat_data, 'u_tower_count', 'u_towers', 100, 2)