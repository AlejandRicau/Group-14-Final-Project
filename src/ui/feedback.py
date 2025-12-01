import arcade


class FloatingMessage:
    """
    A floating UI element that can show text and an optional icon.
    """

    def __init__(self, text, x, y, color, font_size=16, velocity_y=1.0, duration=1.5, icon_texture=None):
        self.x = x
        self.y = y
        self.velocity_y = velocity_y
        self.duration = duration
        self.timer = duration
        self.alpha = 255

        # 1. Setup Text
        # We force anchor_x="left" so we can calculate the width growing to the right
        self.text_obj = arcade.Text(
            text,
            x, y,
            color,
            font_size=font_size,
            anchor_x="left" if icon_texture else "center",
            anchor_y="center",
            font_name="Kenney Future",
            bold=True
        )

        # 2. Setup Icon
        self.icon_list = None
        self.icon_sprite = None

        if icon_texture:
            self.icon_sprite = arcade.Sprite(icon_texture)

            # --- FIX: Scale down (0.25 is 1/4 original size) ---
            self.icon_sprite.scale = 0.25

            # --- FIX: Position to the RIGHT of text ---
            # Get the width of the text we just created
            text_width = self.text_obj.content_width

            # Place icon: Start X + Text Width + Padding (10px) + Half Icon Width
            self.icon_sprite.center_x = x + text_width + 10
            self.icon_sprite.center_y = y

            self.icon_list = arcade.SpriteList()
            self.icon_list.append(self.icon_sprite)

    def update(self, delta_time):
        # Move Up
        move_amount = self.velocity_y * (delta_time * 60)
        self.y += move_amount

        # Update Text Y
        self.text_obj.y = self.y

        # Update Icon Y (Keep X the same)
        if self.icon_sprite:
            self.icon_sprite.center_y = self.y

        # Update Timer
        self.timer -= delta_time

        # Calculate Alpha
        if self.timer < self.duration * 0.5:
            ratio = self.timer / (self.duration * 0.5)
            self.alpha = int(255 * ratio)
            if self.alpha < 0: self.alpha = 0

        # Apply Alpha
        c = self.text_obj.color
        self.text_obj.color = (c[0], c[1], c[2], self.alpha)

        if self.icon_sprite:
            self.icon_sprite.alpha = self.alpha

        return self.timer <= 0

    def draw(self):
        if self.icon_list:
            self.icon_list.draw()
        self.text_obj.draw()