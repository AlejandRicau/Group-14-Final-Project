from src.constants import *
import os
from pathlib import Path
from cryptography.fernet import Fernet

SAVE_FILE = Path("highscore.dat")
KEY_FILE = Path("secret.key")


class GameManager:
    def __init__(self):
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.score = 0

        # 1. Load (or Create) the Encryption Key
        self.key = self._get_key()
        self.cipher = Fernet(self.key)

        self.high_score = self.load_high_score()

    def _get_key(self):
        """
        Checks if a key file exists.
        If yes: Loads it.
        If no: Generates a new random key and saves it.
        """
        if KEY_FILE.exists():
            try:
                with open(KEY_FILE, "rb") as f:
                    return f.read()
            except:
                # If key file is corrupt, regenerate
                pass

        # Generate new key
        new_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(new_key)
        return new_key

    def load_high_score(self):
        """Reads and decrypts the high score."""
        if SAVE_FILE.exists():
            try:
                with open(SAVE_FILE, "rb") as f:
                    encrypted_data = f.read()

                # Decrypt using the loaded key
                decrypted_data = self.cipher.decrypt(encrypted_data)
                return int(decrypted_data.decode())

            except Exception as e:
                print(f"Save file invalid or key mismatch. Resetting score. {e}")
                return 0
        return 0

    def save_high_score(self, new_score):
        """Encrypts and saves the score if it's a record."""
        if new_score > self.high_score:
            self.high_score = new_score

            try:
                # Encrypt
                data_to_save = str(self.high_score).encode()
                encrypted_data = self.cipher.encrypt(data_to_save)

                with open(SAVE_FILE, "wb") as f:
                    f.write(encrypted_data)
                return True
            except Exception as e:
                print(f"Failed to save score: {e}")

        return False

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