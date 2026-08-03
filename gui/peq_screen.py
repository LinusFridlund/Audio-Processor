"""PEQ preset screen: a vertical list of preset rows, each laid out as
CSS `justify-content: space-between` would with 3 flex children — a
name label, a status tag, and a fixed-size mini response-curve graph —
reproduced from the `<div class="card" style="...justify-content:
space-between...">` block and `computeMiniCurve` in the source file.
"""

import math

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Line

import theme
from card import CardButton
from tag import Tag
from svg_fit import ViewBoxFit

PRESET_DEFS = [
    {"id": "default", "name": "Default", "bands": []},
    {"id": "flat", "name": "Flat", "bands": []},
    {"id": "bass-boost", "name": "Bass Boost", "bands": [
        {"freq": 60, "gain": 4, "q": 0.8}, {"freq": 120, "gain": 2, "q": 0.9},
    ]},
    {"id": "vocal", "name": "Vocal Boost", "bands": [
        {"freq": 1500, "gain": 3, "q": 1.1}, {"freq": 3000, "gain": 2, "q": 1.1},
    ]},
    {"id": "night", "name": "Night Mode", "bands": [
        {"freq": 60, "gain": -3, "q": 0.8}, {"freq": 8000, "gain": 1, "q": 0.9},
    ]},
]

ROW_HEIGHT = 92
CURVE_W, CURVE_H = 230, 72
CURVE_VIEWBOX = (0, 0, 160, 50)


def compute_mini_curve(bands):
    w, h = 160, 50
    log_min, log_max = math.log10(20), math.log10(20000)
    points = []
    for i in range(61):
        t = i / 60
        log_f = log_min + t * (log_max - log_min)
        gain = 0.0
        for b in bands:
            sigma = 0.6 / max(b["q"], 0.1)
            dlog = log_f - math.log10(b["freq"])
            gain += b["gain"] * math.exp(-0.5 * (dlog / sigma) ** 2)
        gain = max(-6.0, min(6.0, gain))
        x = t * w
        y = h / 2 - (gain / 6) * (h / 2 - 4)
        points.append((x, y))
    return points


PRESET_CURVES = {p["id"]: compute_mini_curve(p["bands"]) for p in PRESET_DEFS}


class PresetCurveWidget(Widget):
    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.points = points
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        fit = ViewBoxFit(*CURVE_VIEWBOX, self.x, self.y, self.width, self.height)
        self.canvas.clear()
        with self.canvas:
            Color(*theme.NEUTRAL_700)
            p1, p2 = fit.pt(0, 25), fit.pt(160, 25)
            Line(points=[*p1, *p2], width=max(1.0, fit.length(1)))
            Color(*theme.COLOR_ACCENT)
            flat = []
            for vx, vy in self.points:
                flat.extend(fit.pt(vx, vy))
            Line(points=flat, width=max(1.0, fit.length(2)))


class PresetRow(CardButton):
    """Overrides BoxLayout auto-arrangement to reproduce CSS
    `justify-content: space-between` across 3 children of unequal,
    content-driven widths (name label, tag, fixed-size curve)."""

    def __init__(self, preset_id, name, curve_points, on_press_cb, **kwargs):
        super().__init__(
            size_hint=(1, None),
            height=ROW_HEIGHT,
            padding=(theme.SPACE_4, theme.SPACE_4, theme.SPACE_4, theme.SPACE_4),
            **kwargs,
        )
        self.preset_id = preset_id
        self._on_press_cb = on_press_cb

        self.title_label = Label(
            text=name,
            font_name=theme.FONT_HEADING,
            font_size=36,
            color=theme.COLOR_TEXT,
            size_hint=(None, None),
        )
        self.title_label.bind(texture_size=lambda w, ts: setattr(w, "size", ts))

        self.status_tag = Tag("Select", variant="neutral", font_size=14, pad_h=10, pad_v=3)
        self.curve = PresetCurveWidget(curve_points, size_hint=(None, None), size=(CURVE_W, CURVE_H))

        for w in (self.title_label, self.status_tag, self.curve):
            self.add_widget(w)

        self.bind(pos=self._relayout, size=self._relayout)
        self.status_tag.bind(size=self._relayout)
        self.title_label.bind(size=self._relayout)

    def do_layout(self, *args):
        # Bypass BoxLayout's default flow layout — children are placed
        # manually in _relayout to match CSS space-between semantics.
        pass

    def _relayout(self, *args):
        pad_l, pad_t, pad_r, pad_b = self.padding
        content_x = self.x + pad_l
        content_w = self.width - pad_l - pad_r
        cy = self.y + self.height / 2

        w1, w2, w3 = self.title_label.width, self.status_tag.width, self.curve.width
        gap = max(0.0, (content_w - w1 - w2 - w3) / 2)

        x1 = content_x
        x2 = x1 + w1 + gap
        x3 = content_x + content_w - w3

        self.title_label.pos = (x1, cy - self.title_label.height / 2)
        self.status_tag.pos = (x2, cy - self.status_tag.height / 2)
        self.curve.pos = (x3, cy - self.curve.height / 2)

    def set_active(self, active):
        self.set_selected(active)
        self.status_tag.text = "Active" if active else "Select"
        self.status_tag.set_variant("accent" if active else "neutral")
        self._relayout()

    def on_release(self):
        if self._on_press_cb:
            self._on_press_cb(self.preset_id)


class PEQScreen(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(orientation="vertical", spacing=theme.SPACE_3, **kwargs)
        self._on_select = on_select

        kicker = Label(
            text="PEQ PRESET",
            font_name=theme.FONT_BODY,
            font_size=16,
            color=theme.COLOR_ACCENT,
            size_hint=(1, None),
            height=20,
            halign="left",
            valign="middle",
        )
        kicker.bind(size=lambda w, v: setattr(w, "text_size", v))
        self.add_widget(kicker)

        self.rows = {}
        for p in PRESET_DEFS:
            row = PresetRow(p["id"], p["name"], PRESET_CURVES[p["id"]], self._on_select)
            self.rows[p["id"]] = row
            self.add_widget(row)

    def set_active_preset(self, preset_id):
        for pid, row in self.rows.items():
            row.set_active(pid == preset_id)
