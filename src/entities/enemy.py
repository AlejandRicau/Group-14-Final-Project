from src.constants import *
import arcade
import math
from pathlib import Path
from src.ui.indicator_bar import IndicatorBar
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"

class Enemy(arcade.Sprite):
    def __init__(self, path, game_manager, bar_list, health=BASE_ENEMY_HEALTH, damage=ENEMY_PENALTY, speed=BASE_ENEMY_SPEED, reward=ENEMY_REWARD):
        # 1. Load Texture
        super().__init__()
        # --- ANIMATION SETUP ---
        self.walk_right_textures = []
        self.walk_left_textures = []

        for i in range(8):
            tex_path = ASSETS_PATH / "images/characters/ut_zombie" / f"walk_{i}.png"

            # 1. Load Right (Standard)
            tex_r = arcade.load_texture(str(tex_path))
            self.walk_right_textures.append(tex_r)

            # 2. Load Left (Flip the existing texture)
            # FIX: Use .flip_left_right() instead of argument
            tex_l = tex_r.flip_left_right()
            self.walk_left_textures.append(tex_l)

        # Set initial state
        self.cur_texture_index = 0
        self.texture = self.walk_right_textures[0]

        # Animation State
        self.time_since_last_swap = 0.0
        self.animation_speed = 0.1
        self.facing_right = True

        # Scale
        desired_size = TILE_SIZE * 1
        self.scale = desired_size / max(self.texture.width, self.texture.height)

        self.path = path
        self.game_manager = game_manager

        # Stats
        self.max_health = health  # Track Max Health for percentage calc
        self.health = health
        self.damage = damage
        self.speed = speed
        self.reward = reward
        self.current_point_index = 0

        # Setup Health Bar
        # We make it small (width=16) to fit the tile size (20)
        self.indicator_bar = IndicatorBar(
            owner=self,
            sprite_list=bar_list,
            width=16,
            height=2,
            border_size=1,
            full_color=arcade.color.RED,  # Enemies usually have red bars
            background_color=arcade.color.BLACK
        )

        # Set initial position
        if self.path and len(self.path) > 0:
            self.center_x, self.center_y = self.path[0]
            self.indicator_bar.position = (self.center_x, self.center_y + 12)

    def deal_damage(self, ext_damage):
        self.health -= ext_damage

        # Update Health bar
        ratio = self.health / self.max_health
        self.indicator_bar.fullness = ratio

        if self.health <= 0:
            # Give Reward
            self.game_manager.add_money(self.reward)
            self.kill()

    def reach_goal(self):
        # Penalize Player
        self.game_manager.lose_life(self.damage)
        self.kill()

    def kill(self):
        # We must remove the health bar sprites when the enemy is removed!
        if self.indicator_bar:
            self.indicator_bar.kill()
        super().kill()

    def update(self, delta_time: float = 1 / 60):
        # 0. Safety Check
        if not self.path or self.current_point_index >= len(self.path):
            return

            # 1. Navigation Logic
        target_point = self.path[self.current_point_index]
        dest_x, dest_y = target_point

        start_x = self.center_x
        start_y = self.center_y

        x_diff = dest_x - start_x
        y_diff = dest_y - start_y

        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
        move_distance = self.speed * delta_time

        # 2. Determine Facing Direction
        if x_diff > 0.1:
            self.facing_right = True
        elif x_diff < -0.1:
            self.facing_right = False

        # 3. Move
        if distance <= move_distance:
            self.center_x = dest_x
            self.center_y = dest_y
            self.current_point_index += 1
            if self.current_point_index >= len(self.path):
                self.reach_goal()
        else:
            angle_rad = math.atan2(y_diff, x_diff)
            self.center_x += math.cos(angle_rad) * move_distance
            self.center_y += math.sin(angle_rad) * move_distance

        # 4. Animate Texture
        self.time_since_last_swap += delta_time
        if self.time_since_last_swap > self.animation_speed:
            self.time_since_last_swap = 0.0
            self.cur_texture_index += 1

            if self.cur_texture_index >= 8:
                self.cur_texture_index = 0

            if self.facing_right:
                self.texture = self.walk_right_textures[self.cur_texture_index]
            else:
                self.texture = self.walk_left_textures[self.cur_texture_index]

        # 5. Update Health Bar Position
        if self.indicator_bar:
            self.indicator_bar.position = (self.center_x, self.center_y + 12)

    def distance_to(self, other):
        return math.sqrt((self.center_x - other.center_x) ** 2 + (self.center_y - other.center_y) ** 2)
