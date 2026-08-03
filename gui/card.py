"""The `.card` building block from styles.css: a surface-colored,
rounded rect, optionally shown "selected" with an accent-colored ring
(`border-color:accent; box-shadow:0 0 0 1px accent`)."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Line

import theme


class Card(BoxLayout):
    def __init__(self, selected=False, radius=theme.RADIUS_MD, **kwargs):
        super().__init__(**kwargs)
        self.selected = selected
        self.radius = radius
        with self.canvas.before:
            self._bg_color = Color(*theme.COLOR_SURFACE)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            self._border_color = Color(*theme.COLOR_ACCENT)
            self._border_color.a = 1.0 if selected else 0.0
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, radius),
                width=1,
            )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._border.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)

    def set_selected(self, selected):
        self.selected = selected
        self._border_color.a = 1.0 if selected else 0.0


class CardButton(ButtonBehavior, Card):
    """A Card that acts as a clickable button (used for source/preset rows)."""

    pass
