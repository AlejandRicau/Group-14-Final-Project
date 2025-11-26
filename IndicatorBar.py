from constants import *
import arcade
class IndicatorBar:
    """
    Represents a bar which can display information about a sprite.
    """

    def __init__(
            self,
            owner: arcade.Sprite,
            sprite_list: arcade.SpriteList,
            position: tuple[float, float] = (0, 0),
            full_color: arcade.Color = arcade.color.GREEN,
            background_color: arcade.Color = arcade.color.BLACK,
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