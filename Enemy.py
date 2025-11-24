from constants import *
import arcade
import math


class Enemy(arcade.Sprite):
    def __init__(self, path, health=100, damage=10, speed=100, reward=10):
        # 1. Load Texture
        texture = arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png")

        # 2. Calculate Scale using the GLOBAL constant
        # We make it slightly smaller (80%) to fit comfortably in the tile
        desired_size = TILE_SIZE
        scale = desired_size / max(texture.width,texture.height)

        # Pass texture as the first POSITIONAL argument
        super().__init__(texture, scale=scale)
        self.path = path
        self.current_point_index = 0
        self.health = health
        self.damage = damage
        self.speed = speed
        self.reward = reward

        # Set initial position
        if self.path and len(self.path) > 0:
            self.center_x, self.center_y = self.path[0]

    def deal_damage(self, ext_damage):
        self.health -= ext_damage
        if self.health <= 0:
            self.kill()

    def update(self, delta_time: float = 1 / 60):
        if not self.path or self.current_point_index >= len(self.path):
            return

        # 1. Identify Target
        target_point = self.path[self.current_point_index]
        dest_x, dest_y = target_point

        # 2. Calculate Vector
        start_x = self.center_x
        start_y = self.center_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y

        # 3. Move Logic
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
        move_distance = self.speed * delta_time

        if distance <= move_distance:
            # Snap to target
            self.center_x = dest_x
            self.center_y = dest_y
            self.current_point_index += 1

            if self.current_point_index >= len(self.path):
                self.reach_goal()
        else:
            # Move towards target
            angle = math.atan2(y_diff, x_diff)
            self.center_x += math.cos(angle) * move_distance
            self.center_y += math.sin(angle) * move_distance

    def reach_goal(self):
        print(f"Enemy reached goal! Dealt {self.damage} damage.")
        self.kill()