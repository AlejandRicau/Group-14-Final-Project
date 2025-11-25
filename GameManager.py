from constants import *

class GameManager:
    def __init__(self):
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.score = 0

    def can_afford(self, cost):
        """Checks if the player has enough money."""
        return self.money >= cost

    def spend_money(self, cost):
        """Deducts money if affordable. Returns True if successful."""
        if self.money >= cost:
            self.money -= cost
            return True
        return False

    def add_money(self, amount):
        self.money += amount
        self.score += amount # Optional: Score increases with money earned

    def lose_life(self, amount=1):
        self.lives -= amount
        if self.lives < 0:
            self.lives = 0
            # Logic for Game Over can be added here later