from constants import *
import arcade
import math


class IndicatorBar:
    """
    Represents a bar which can display information about a sprite.
    """

    def __init__(
            self,
            owner: arcade.Sprite,
            sprite_list: arcade.SpriteList,
            position: tuple[float, float] = (0, 0),
            full_color = arcade.color.GREEN,
            background_color = arcade.color.BLACK,
            width: int = 100,
            height: int = 4,
            border_size: int = 4,
            scale: tuple[float, float] = (1.0, 1.0),
    ) -> None:
        self.owner = owner
        self.sprite_list = sprite_list
        self._bar_width = width
        self._bar_height = height
        self._center_x = 0.0
        self._center_y = 0.0
        self._fullness = 0.0
        self._scale = scale

        # Create the boxes
        self._background_box = arcade.SpriteSolidColor(
            self._bar_width + border_size,
            self._bar_height + border_size,
            color=background_color,
        )
        self._full_box = arcade.SpriteSolidColor(
            self._bar_width,
            self._bar_height,
            color=full_color,
        )
        self.sprite_list.append(self._background_box)
        self.sprite_list.append(self._full_box)

        self.fullness = 1.0
        self.position = position
        self.scale = scale

    @property
    def fullness(self) -> float:
        return self._fullness

    @fullness.setter
    def fullness(self, new_fullness: float) -> None:
        if not (0.0 <= new_fullness <= 1.0):
            # Clamp value instead of raising error to prevent crashes during rapid damage
            new_fullness = max(0.0, min(1.0, new_fullness))

        self._fullness = new_fullness
        if new_fullness == 0.0:
            self._full_box.visible = False
        else:
            self._full_box.visible = True
            self._full_box.width = self._bar_width * new_fullness * self._scale[0]
            self._full_box.left = self._center_x - (self._bar_width / 2) * self._scale[0]

    @property
    def position(self) -> tuple[float, float]:
        return self._center_x, self._center_y

    @position.setter
    def position(self, new_position: tuple[float, float]) -> None:
        self._center_x, self._center_y = new_position
        self._background_box.position = new_position
        self._full_box.position = new_position
        self._full_box.left = self._center_x - (self._bar_width / 2) * self._scale[0]

    # Helper to clean up sprites when enemy dies
    def kill(self):
        self._background_box.kill()
        self._full_box.kill()


class Enemy(arcade.Sprite):
    def __init__(self, path, game_manager, bar_list, health=100, damage=10, speed=100, reward=10):
        # 1. Load Texture
        texture = arcade.load_texture(":resources:images/animated_characters/zombie/zombie_idle.png")
        desired_size = TILE_SIZE * 0.8
        scale = desired_size / max(texture.width, texture.height)
        super().__init__(texture, scale=scale)

        self.path = path
        self.game_manager = game_manager

        # Stats
        self.max_health = health  # Track Max Health for percentage calc
        self.health = health
        self.damage = damage
        self.speed = speed
        self.reward = reward
        self.current_point_index = 0

        # --- NEW: Setup Health Bar ---
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
        print(f"Enemy reached goal! Dealt {self.damage} damage.")
        # Penalize Player
        self.game_manager.lose_life(1)
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

        # 1. Identify Target
        target_point = self.path[self.current_point_index]
        dest_x, dest_y = target_point

        # 2. Calculate Vector
        start_x = self.center_x
        start_y = self.center_y
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y

        # 3. Calculate Distance and Speed
        distance = math.sqrt(x_diff ** 2 + y_diff ** 2)
        move_distance = self.speed * delta_time

        # 4. Movement Angle (Math only, no visual rotation)
        angle_rad = math.atan2(y_diff, x_diff)

        # --- REMOVED: self.angle = math.degrees(angle_rad) ---
        # We just leave self.angle alone (it defaults to 0)

        # 5. Move Logic
        if distance <= move_distance:
            # Snap to target
            self.center_x = dest_x
            self.center_y = dest_y
            self.current_point_index += 1

            if self.current_point_index >= len(self.path):
                self.reach_goal()
        else:
            # Move smoothly using the calculated radian angle
            self.center_x += math.cos(angle_rad) * move_distance
            self.center_y += math.sin(angle_rad) * move_distance

        # 6. Update Health Bar Position
        if self.indicator_bar:
            self.indicator_bar.position = (self.center_x, self.center_y + 12)

    def distance_to(self, other):
        return math.sqrt((self.center_x - other.center_x) ** 2 + (self.center_y - other.center_y) ** 2)
