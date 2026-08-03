"""The `.tag` chip from styles.css — a small rounded pill of text.
Sizes itself to its text (`fit-content`, matching the source markup).
"""

from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line

import theme

VARIANTS = {
    # (background, text_color, border_color_or_None)
    "accent": (theme.ACCENT_800, theme.ACCENT_100, None),
    "neutral": (theme.NEUTRAL_800, theme.NEUTRAL_100, None),
    "outline": (None, theme.COLOR_ACCENT, theme.COLOR_ACCENT),
}


class Tag(Label):
    def __init__(
        self,
        text="",
        variant="neutral",
        font_size=11,
        pad_h=10,
        pad_v=3,
        **kwargs,
    ):
        kwargs.setdefault("font_name", theme.FONT_BODY)
        kwargs.setdefault("size_hint", (None, None))
        super().__init__(text=text, font_size=font_size, **kwargs)
        self.variant = variant
        self.pad_h = pad_h
        self.pad_v = pad_v
        self.bind(texture_size=self._resize, pos=self._redraw)
        self._apply_variant()
        self._resize()

    def _apply_variant(self):
        bg, fg, border = VARIANTS.get(self.variant, VARIANTS["neutral"])
        self._bg = bg
        self.color = fg
        self._border = border

    def set_variant(self, variant):
        self.variant = variant
        self._apply_variant()
        self._redraw()

    def _resize(self, *args):
        self.size = (self.texture_size[0] + self.pad_h * 2, self.texture_size[1] + self.pad_v * 2)
        self._redraw()

    def _redraw(self, *args):
        self.canvas.before.clear()
        radius = 6
        with self.canvas.before:
            if self._bg is not None:
                Color(*self._bg)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            if self._border is not None:
                Color(*self._border)
                Line(
                    rounded_rectangle=(self.x, self.y, self.width, self.height, radius),
                    width=1,
                )
