"""Top bar: screen title on the left, three status chips pinned right
(source, sample-rate/format, active PEQ preset)."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line

import theme
from tag import Tag

HEADER_HEIGHT = 56


class Header(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=HEADER_HEIGHT,
            padding=(theme.SPACE_5, 0, theme.SPACE_5, 0),
            spacing=theme.SPACE_3,
            **kwargs,
        )
        with self.canvas.after:
            Color(*theme.NEUTRAL_800)
            self._border = Line(points=[0, 0, 0, 0], width=1)
        self.bind(pos=self._sync_border, size=self._sync_border)

        self.title_label = Label(
            text="",
            font_name=theme.FONT_HEADING,
            font_size=30,
            color=theme.COLOR_TEXT,
            size_hint=(None, 1),
            halign="left",
            valign="middle",
        )
        self.title_label.bind(texture_size=lambda w, v: setattr(w, "width", v[0]))
        self.title_label.bind(size=lambda w, v: setattr(w, "text_size", (None, v[1])))
        self.add_widget(self.title_label)

        self.add_widget(Widget())  # margin-left: auto spacer

        tag_row = BoxLayout(orientation="horizontal", size_hint=(None, 1), spacing=theme.SPACE_3)
        self.source_tag = Tag("", variant="outline", font_size=20, pad_h=13, pad_v=7)
        self.format_tag = Tag("", variant="neutral", font_size=20, pad_h=13, pad_v=7)
        self.preset_tag = Tag("", variant="accent", font_size=20, pad_h=13, pad_v=7)
        for t in (self.source_tag, self.format_tag, self.preset_tag):
            t.pos_hint = {"center_y": 0.5}
            tag_row.add_widget(t)
        tag_row.bind(minimum_width=lambda w, v: setattr(w, "width", v))
        self.add_widget(tag_row)

    def _sync_border(self, *args):
        y = self.y
        self._border.points = [self.x, y, self.x + self.width, y]

    def set_values(self, title, source_label, format_label, preset_label):
        self.title_label.text = title
        self.source_tag.text = source_label
        self.format_tag.text = format_label
        self.preset_tag.text = preset_label
