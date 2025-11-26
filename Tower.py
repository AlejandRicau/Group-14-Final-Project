from constants import *
from helper_functions import *
from Enemy import Enemy
import arcade

class Tower(arcade.Sprite):
    def __init__(self, tile, range_r, freq, damage):
        super().__init__()
        self.tile = tile
        self.level = 1

        self.range_radius = range_r
        self.range_display = None
        self.create_range_display()

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
        self.target_dot = arcade.SpriteCircle(5, arcade.color.RED)
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

    def attack_update(self, delta_time: float):
        """Manage cooldown and return immediately if no target"""
        # Count down cooldown and return if no target
        self.cooldown = max(0.0, self.cooldown - delta_time)
        if self.on_target is None:
            return

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

    def attack_update(self, delta_time: float):
        """
        Attack the target enemy alone
        """
        super().attack_update(delta_time)

        if self.cooldown <= 0 and self.on_target:
            # Fire!
            self.on_target.deal_damage(self.damage)

            # Reset cooldown
            self.cooldown = 1.0 / self.frequency



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

    def attack_update(self, delta_time: float):
        """
        Attack all enemies within the AOE radius
        """
        super().attack_update(delta_time)

        if self.cooldown <= 0 and self.on_target:
            # Fire! Damage all enemies in the list
            for enemy in self.damage_enemy_list:
                enemy.deal_damage(self.damage)

            # Reset cooldown
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



class ChainTower(Tower):
    def __init__(self, tile):
        super().__init__(
            tile,
            range_r = CHAIN_TOWER_RANGE_RADIUS,
            freq = CHAIN_TOWER_FREQUENCY,
            damage = CHAIN_TOWER_DAMAGE
        )
        self.texture = TOWER_TEXTURES['chain']

        # Chain specific variables
        self.chain_enemy_list : list[Enemy] = []
        self.is_chain_list_complete = False
        self.chain_length = CHAIN_TOWER_CHAIN_LENGTH

    def attack_update(self, delta_time: float):
        """
        Attack all enemies in the chain
        """
        super().attack_update(delta_time)

        if self.cooldown <= 0 and self.is_chain_list_complete:
            # Fire! Damage all enemies in the list
            for enemy in self.chain_enemy_list:
                enemy.deal_damage(self.damage)
                self.is_chain_list_complete = False

            # Reset cooldown
            self.cooldown = 1.0 / self.frequency

    def acquire_target(self, enemy_list: list[Enemy]):
        """
        Acquire all enemies within the AOE radius
        """
        # Acquire the closest enemy and return if none
        super().acquire_target(enemy_list)
        if self.on_target is None:
            return

        # duplicate the enemy list
        chained_candidates = list(enemy_list)
        self.is_chain_list_complete = False

        # Iteratively find all enemies along the chain
        curr = self.on_target
        while chained_candidates:
            # Add the current enemy to the chain then remove it from the candidate list
            self.chain_enemy_list.append(curr)
            chained_candidates.remove(curr)

            # Stop if no more candidates
            if not chained_candidates:
                self.is_chain_list_complete = True
                break

            # Find the closest enemy to the current enemy
            next_enemy = min(
                chained_candidates,
                key=lambda e: curr.distance_to(e)
            )

            # Check if the next enemy is within the chain length
            if curr.distance_to(next_enemy) > self.chain_length:
                self.is_chain_list_complete = True      # Mark the chain list as complete#
                break
            curr = next_enemy       # Move to the next enemy