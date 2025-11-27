import random
from constants import *


class WaveManager:
    def __init__(self, game_view):
        self.game = game_view  # Reference to the main game to call methods
        self.current_wave = 0

        # State: "BETWEEN_WAVES", "SPAWNING", "WAITING_FOR_CLEAR"
        self.state = "BETWEEN_WAVES"

        # Timers
        self.time_between_waves = 5.0  # Seconds break before next wave
        self.timer = self.time_between_waves

        # Wave Data
        self.enemies_to_spawn = 0
        self.spawn_interval = 0
        self.spawn_timer = 0
        self.current_speed = 0

    def start_next_wave(self):
        """Calculates all the numbers for the upcoming wave."""
        self.current_wave += 1
        print(f"--- STARTING WAVE {self.current_wave} ---")

        # 1. Apply Map Changes based on curves
        if self.current_wave > 1:  # Don't expand on wave 1
            self.apply_map_changes()

        # 2. Calculate Enemy Data
        self.enemies_to_spawn = GET_ENEMY_COUNT(self.current_wave)
        self.spawn_interval = GET_SPAWN_INTERVAL(self.current_wave)
        self.current_speed = GET_ENEMY_SPEED(self.current_wave)

        self.state = "SPAWNING"
        self.spawn_timer = 0

    def apply_map_changes(self):
        """Checks the curves and modifies the map if needed."""
        map_changed = False

        # Expansion
        if SHOULD_EXPAND(self.current_wave):
            print(">>> MAP EXPANDING!")
            self.game.map.expand_map(add_width=6, add_height=6)
            self.game.rebuild_background_list()
            map_changed = True

        # New Spawn
        if SHOULD_ADD_SPAWN(self.current_wave):
            print(">>> NEW SPAWN ADDED!")
            self.game.map.generate_new_special_point("spawn")
            self.game.rebuild_background_list()
            map_changed = True

        # New Goal
        if SHOULD_ADD_GOAL(self.current_wave):
            print(">>> NEW GOAL ADDED!")
            self.game.map.generate_new_special_point("goal")
            self.game.rebuild_background_list()
            map_changed = True

        if map_changed:
            # Important: Rebuild the view and recalculate paths
            self.game.map.calculate_autotiling()
            self.game.rebuild_background_list()
            # Clear existing enemies/towers if necessary or handle logic
            # (Usually we wait until wave is cleared to expand, so it's safe)

    def update(self, delta_time):

        # STATE 1: Counting down to next wave
        if self.state == "BETWEEN_WAVES":
            self.timer -= delta_time
            if self.timer <= 0:
                self.start_next_wave()

        # STATE 2: Spawning Enemies
        elif self.state == "SPAWNING":
            self.spawn_timer -= delta_time
            if self.spawn_timer <= 0:
                self.trigger_spawn()
                self.spawn_timer = self.spawn_interval

            if self.enemies_to_spawn <= 0:
                self.state = "WAITING_FOR_CLEAR"

        # STATE 3: Waiting for player to kill them all
        elif self.state == "WAITING_FOR_CLEAR":
            if len(self.game.enemy_list) == 0:
                print("Wave Cleared!")
                self.game.game_manager.add_money(50)  # Wave Clear Bonus
                self.state = "BETWEEN_WAVES"
                self.timer = self.time_between_waves

    def trigger_spawn(self):
        """Tells the GameView to spawn 1 enemy."""
        if not self.game.map.spawns:
            return

        # Pick a random spawn point if we have multiple
        start_tile = random.choice(self.game.map.spawns)

        # Call the existing method in GameView
        # We need to modify GameView.spawn_enemy_at_tile to accept speed
        self.game.spawn_enemy_at_tile(start_tile, self.current_speed)

        self.enemies_to_spawn -= 1