"""Left nav rail: VU / Spectrum / Source / PEQ buttons + an "Encoder"
hint pinned to the bottom (`margin-top: auto` in the source markup).
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line

import theme
from icons import IconWidget

SIDEBAR_WIDTH = 126

NAV_ITEMS = [
    ("vu", "vu", "VU"),
    ("fft", "spectrum", "Spectrum"),
    ("source", "source", "Source"),
    ("peq", "peq", "PEQ"),
]


class NavButton(ButtonBehavior, BoxLayout):
    def __init__(self, icon, label, on_press_cb, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=8,
            padding=(4, 12, 4, 12),
            size_hint=(1, None),
            height=29 + 8 + 26 + 24,
            **kwargs,
        )
        self._on_press_cb = on_press_cb
        self.active = False

        with self.canvas.before:
            self._bg_color = Color(0, 0, 0, 0)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[theme.RADIUS_MD])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        self.icon_widget = IconWidget(icon=icon, color=theme.NEUTRAL_300, size_hint=(1, None), height=29)
        self.label_widget = Label(
            text=label,
            font_name=theme.FONT_BODY,
            font_size=20,
            color=theme.NEUTRAL_300,
            size_hint=(1, None),
            height=26,
        )
        self.add_widget(self.icon_widget)
        self.add_widget(self.label_widget)

    def _sync_bg(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def set_active(self, active):
        self.active = active
        if active:
            self._bg_color.rgba = theme.ACCENT_800
            color = theme.ACCENT_300
        else:
            self._bg_color.rgba = (0, 0, 0, 0)
            color = theme.NEUTRAL_300
        self.icon_widget.set_color(color)
        self.label_widget.color = color

    def on_release(self):
        if self._on_press_cb:
            self._on_press_cb()


class Sidebar(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, 1),
            width=SIDEBAR_WIDTH,
            padding=(theme.SPACE_2, theme.SPACE_4, theme.SPACE_2, theme.SPACE_4),
            spacing=theme.SPACE_3,
            **kwargs,
        )
        self._on_select = on_select
        self.buttons = {}

        with self.canvas.after:
            Color(*theme.NEUTRAL_800)
            self._border = Line(points=[0, 0, 0, 0], width=1)
        self.bind(pos=self._sync_border, size=self._sync_border)

        for screen_id, icon, label in NAV_ITEMS:
            btn = NavButton(icon, label, lambda sid=screen_id: self._on_select(sid))
            self.buttons[screen_id] = btn
            self.add_widget(btn)

        self.add_widget(Widget(size_hint=(1, 1)))

        encoder_box = BoxLayout(
            orientation="vertical",
            spacing=5,
            padding=(0, theme.SPACE_3, 0, 0),
            size_hint=(1, None),
            height=20 + 5 + 34 + theme.SPACE_3,
            opacity=0.45,
        )
        encoder_box.add_widget(IconWidget(icon="encoder", color=theme.COLOR_TEXT, size_hint=(1, None), height=20))
        encoder_box.add_widget(
            Label(
                text="Encoder",
                font_name=theme.FONT_BODY,
                font_size=13,
                color=theme.COLOR_TEXT,
                size_hint=(1, None),
                height=34,
                halign="center",
                valign="middle",
            )
        )
        # Label halign needs text_size bound to width to actually center.
        lbl = encoder_box.children[0]
        lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        self.add_widget(encoder_box)

    def set_active_screen(self, screen_id):
        for sid, btn in self.buttons.items():
            btn.set_active(sid == screen_id)

    def _sync_border(self, *args):
        x = self.x + self.width
        self._border.points = [x, self.y, x, self.y + self.height]
