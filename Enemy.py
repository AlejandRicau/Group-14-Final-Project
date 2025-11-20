from constants import *
from helper_functions import *

class Enemy(arcade.Sprite):
    def __init__(self, tile):
        super().__init__()
        self.position = None