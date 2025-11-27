from helper_functions import *
from visual_effect import *
from constants import *
from Enemy import Enemy
import arcade

class Tower(arcade.Sprite):
    def __init__(self, tile, range_r, freq, damage):
        super().__init__()
        self.tile = tile
        self.level = 1

        # create the tower range visual
        self.range_radius = range_r
        self.range_display = None
        self.create_range_display()

        # create the tower target dot visual
        self.target_dot = None
        self.create_target_dot()

        self.frequency = freq       #<-- How often the tower attacks [1/second]
        self.on_target: Enemy | None = None       #<-- Enemy currently being targeted
        self.damage = damage
        self.cooldown = 0.0

        # Set the tower's position to the tile's center
        self.center_x = tile.center_x
        self.center_y = tile.center_y

    def update(self, *args, **kwargs):
        """
        Updates the tower's internal logic
        """
        self.update_position_for_map_expansion()
        self.update_display_texture()
        self.update_target_dot()

    def update_position_for_map_expansion(self):
        """
        Updates the tower's position to the tile's center, made for map expansion
        """
        # Keep tower centered on its tile
        self.center_x = self.tile.center_x
        self.center_y = self.tile.center_y

        # Update range display
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

    def create_range_display(self):
        """
        Creates a circular range display as a Sprite with a proper hitbox
        """
        # Create a circle texture
        diameter = self.range_radius * 2
        circle_tex = arcade.make_circle_texture(diameter, arcade.color.GRAY)

        # Create a Sprite with that texture
        self.range_display = arcade.Sprite()
        self.range_display.texture = circle_tex

        # Set position
        self.range_display.center_x = self.tile.center_x
        self.range_display.center_y = self.tile.center_y

        # Make it semi-transparent
        self.range_display.alpha = RANGE_DISPLAY_OPACITY

    def toggle_range_display(self):
        """Hide or show the range display"""
        self.range_display.visible = not self.range_display.visible

    def update_display_texture(self):
        """Updates the range display texture based on the tower's state"""
        # If tower is on target, color red, else gray
        if self.on_target:
            color = arcade.color.RED
        else:
            color = arcade.color.GRAY

        # Replace the texture dynamically
        diameter = self.range_radius * 2
        new_tex = arcade.make_circle_texture(diameter, color)
        self.range_display.texture = new_tex
        self.range_display.alpha = RANGE_DISPLAY_OPACITY

    def acquire_target(self, enemy_list):
        """
        Acquires the closest enemy within range

        Args:
            enemy_list (list): List of all enemies from the game/window
        """
        # Initialize variables
        closest = None
        min_dist_sq = self.range_radius * self.range_radius

        # Iterate through all enemies
        for enemy in enemy_list:
            dx = self.center_x - enemy.center_x
            dy = self.center_y - enemy.center_y
            dist_sq = dx*dx + dy*dy

            # Update the closest enemy if within range and closer
            if dist_sq <= min_dist_sq and (closest is None or dist_sq < min_dist_sq):
                closest = enemy
                min_dist_sq = dist_sq

        self.on_target = closest

    def create_target_dot(self):
        """Creates a circular target aim as a Sprite"""
        self.target_dot = arcade.SpriteCircle(TARGET_DOT_RADIUS, arcade.color.RED)
        self.target_dot.visible = False     # Make it invisible
        self.target_dot.center_x = self.tile.center_x
        self.target_dot.center_y = self.tile.center_y

    def update_target_dot(self):
        """Updates the target dot's position to the tower's tile"""
        if self.on_target:
            self.target_dot.center_x = self.on_target.center_x
            self.target_dot.center_y = self.on_target.center_y
            self.target_dot.visible = True
        else:
            self.target_dot.center_x = self.center_x
            self.target_dot.center_y = self.center_y
            self.target_dot.visible = False

    def _fire_condition(self, delta_time: float):
        """
        Update the cooldown timer.
        Returns True if the tower is ready to attack this frame.
        """
        # Reduce cooldown
        self.cooldown = max(0.0, self.cooldown - delta_time)

        # Early exit conditions
        if self.on_target is None:
            return False  # no target, cannot fire
        if self.cooldown > 0:
            return False  # still cooling down

        # Cooldown expired and target exists
        return True

    def upgrade(self):
        self.level += 1



class BaseTower(Tower):
    def __init__(self, tile):
        super().__init__(
            tile,
            range_r = BASE_TOWER_RANGE_RADIUS,
            freq = BASE_TOWER_FREQUENCY,
            damage = BASE_TOWER_DAMAGE
        )
        self.texture = TOWER_TEXTURES['base']

    def attack_update(self, delta_time, visual_effect_list):
        """
        Attack the target enemy alone

        Args:
            delta_time (float): Time elapsed since last frame
            visual_effect_list (list): List of all visual effects in the game
        """
        # Early exit if not ready to attack
        if not super()._fire_condition(delta_time): return

        '''add visual effect'''
        # Add steam puff centered around the tower when shooting
        visual_effect_list.append(
            SteamPuff(
                self.center_x,
                self.center_y))

        # Add bullet
        visual_effect_list.append(
            Bullet(
                self.center_x,
                self.center_y,
                self.on_target.center_x,
                self.on_target.center_y))

        # Add smaller steam puff centered around the target when shooting
        visual_effect_list.append(
            SteamPuff(
                self.on_target.center_x,
                self.on_target.center_y,
                size=3))

        # deal damage to the target
        self.on_target.deal_damage(self.damage)
        self.cooldown = 1.0 / self.frequency        # Reset cooldown



class AOETower(Tower):
    def __init__(self, tile):
        super().__init__(
            tile,
            range_r = AOE_RANGE_RADIUS,
            freq = AOE_FREQUENCY,
            damage=AOE_DAMAGE
        )
        self.texture = TOWER_TEXTURES['AOE']

        # AOE specific variables
        self.AOE_radius = AOE_DAMAGE_RADIUS
        self.damage_enemy_list : list[Enemy] = []
        self.boom_trajectory_visual_effect = None

    def attack_update(self, delta_time, visual_effect_list):
        """
        Attack all enemies within the AOE radius

        args:
            delta_time (float): Time elapsed since last frame
            visual_effect_list (list): List of all visual effects in the game
        """
        # reset the trajectory
        if (self.boom_trajectory_visual_effect
                and self.boom_trajectory_visual_effect.can_be_removed):
            self.boom_trajectory_visual_effect = None

        # Early exit if not ready to attack
        if not super()._fire_condition(delta_time):
            if self.boom_trajectory_visual_effect and self.on_target :
                self.boom_trajectory_visual_effect.target_x = self.on_target.center_x
                self.boom_trajectory_visual_effect.target_y = self.on_target.center_y
            return

        '''add visual effect'''
        # Add steam puff centered around the tower when shooting
        visual_effect_list.append(
            SteamPuff(
                self.center_x,
                self.center_y,
                size=20))

        # Add steam boom and store it as an attribute
        self.boom_trajectory_visual_effect = SteamBoom(
                self.center_x,
                self.center_y,
                self.on_target.center_x,
                self.on_target.center_y)
        visual_effect_list.append(self.boom_trajectory_visual_effect)


        # Add steam puff centered around the target
        visual_effect_list.append(
            SteamPuff(
                self.on_target.center_x,
                self.on_target.center_y,
                size=15))

        # Fire! Damage all enemies in the list
        for enemy in self.damage_enemy_list:
            enemy.deal_damage(self.damage)

        # Reset cooldown
        self.damage_enemy_list.clear()
        self.cooldown = 1.0 / self.frequency

    def acquire_target(self, enemy_list):
        """
        Acquire all enemies within the AOE radius
        """
        # Acquire the closest enemy
        super().acquire_target(enemy_list)

        # check if the closest enemy is within the AOE radius
        if self.on_target is None:
            return

        # Acquire all enemies within the AOE radius
        self.damage_enemy_list = []
        for enemy in enemy_list:
            dx = enemy.center_x - self.on_target.center_x
            dy = enemy.center_y - self.on_target.center_y
            dist_sq = dx*dx + dy*dy
            if dist_sq <= self.AOE_radius * self.AOE_radius:    #<-- If enemy is within AOE radius
                self.damage_enemy_list.append(enemy)        #<-- Add enemy to the list



class LaserTower(Tower):
    def __init__(self, tile):
        super().__init__(
            tile,
            range_r = LASER_TOWER_RANGE_RADIUS,
            freq = LASER_TOWER_FREQUENCY,
            damage = LASER_TOWER_DAMAGE
        )
        self.texture = TOWER_TEXTURES['laser']

        # Laser specific variables
        self.laser_enemy_list : list[Enemy] = []
        self.is_laser_list_complete = False
        self.laser_length = LASER_TOWER_BEAM_LENGTH
        self.pt_beam_end = (0, 0)

    def attack_update(self, delta_time, visual_effect_list):
        """
        Attack all enemies in the chain

        args:
            delta_time (float): Time elapsed since last frame
            visual_effect_list (list): List of all visual effects in the game
        """
        # Early exit conditions
        if not self._fire_condition(delta_time): return

        # Create visual effect
        x_end, y_end = self.pt_beam_end
        laser_effect = LaserEffect(
            self.center_x, self.center_y,
            x_end, y_end)

        visual_effect_list.append(laser_effect)     #<-- Add visual effect to the list

        # Fire! Damage all enemies in the list
        for enemy in self.laser_enemy_list:
            enemy.deal_damage(self.damage)

        # Reset laser list and cooldown
        self.laser_enemy_list.clear()
        self.cooldown = 1.0 / self.frequency        #<-- Reset cooldown

    def acquire_target(self, enemy_list: list[Enemy]):
        """
        Acquire all enemies within the AOE radius
        """
        # Acquire the closest enemy and return if none
        super().acquire_target(enemy_list)
        if self.on_target is None:
            return

        '''create beam geometry'''
        # create vector of the tower to the target
        dx = self.on_target.center_x - self.center_x
        dy = self.on_target.center_y - self.center_y

        # normalize the vector
        length = (dx*dx + dy*dy) ** 0.5
        dx /= length
        dy /= length

        # multiply the vector by the beam length
        x_beam_end = self.center_x + dx * self.laser_length
        y_beam_end = self.center_y + dy * self.laser_length
        self.pt_beam_end = (x_beam_end, y_beam_end)     #<-- Store the end point of the beam

        '''add enemy to the list if it's on the beam'''
        self.laser_enemy_list = []
        for enemy in enemy_list:
            dist_to_beam = distance_point_to_segment(
                enemy.center_x, enemy.center_y,
                self.center_x, self.center_y,
                x_beam_end, y_beam_end
            )
            if dist_to_beam <= TILE_SIZE / 2:
                self.laser_enemy_list.append(enemy)