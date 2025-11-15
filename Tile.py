class Tile:
    def __init__(self, x, y, color=0):
        self.x = x
        self.y = y
        self._is_spawn = False
        self._is_goal = False
        self._is_border = False
        self._is_path = False

    '''Clear state method'''
    # clear the state of tile every time there is a state update
    def _clear_states(self):
        self._is_spawn = False
        self._is_goal = False
        self._is_border = False
        self._is_path = False

    '''Update color based on tile type'''
    @property
    def color(self):
        if self.is_border:
            return 4
        elif self.is_goal:
            return 3
        elif self.is_spawn:
            return 2
        elif self.is_path:
            return 1
        else:
            return 0

    '''Spawn Property'''
    @property
    def is_spawn(self):
        return self._is_spawn

    @is_spawn.setter
    def is_spawn(self, value):
        if value:  # Only clear when turning on
            self._clear_states()
        self._is_spawn = value

    '''Goal Property'''
    @property
    def is_goal(self):
        return self._is_goal

    @is_goal.setter
    def is_goal(self, value):
        if value:  # Only clear when turning on
            self._clear_states()
        self._is_goal = value

    '''Border Property'''
    @property
    def is_border(self):
        return self._is_border

    @is_border.setter
    def is_border(self, value):
        if value:
            self._clear_states()
        self._is_border = value

    '''Path Property'''
    @property
    def is_path(self):
        return self._is_path

    @is_path.setter
    def is_path(self, value):
        if value:  # Only clear when turning on
            self._clear_states()
        self._is_path = value

    '''Clear Methods'''

    def clear_spawn(self):
        self._is_spawn = False

    def clear_goal(self):
        self._is_goal = False

    def clear_border(self):
        self._is_border = False

    def clear_path(self):
        self._is_path = False
