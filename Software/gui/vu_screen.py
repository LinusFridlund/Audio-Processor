"""VU meters screen: two flat-vector analog-style gauges (Left/Right),
ported from the gauge math in the `<script>` block of
`Device Display.dc.html` (angleForLevel / gaugePoint / buildStaticGauge).
"""

import math

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Ellipse

import theme
from svg_fit import ViewBoxFit

VU_MIN, VU_MAX = -40, 0
MAJOR_LEVELS = [-40, -20, -10, 0]
MINOR_LEVELS = [-30, -15, -8, -6, -4, -2]
PIVOT_X, PIVOT_Y = 100, 142
ANGLE_MIN, ANGLE_MAX = 135, 45
VIEWBOX = (-15, -14, 215, 182)  # minx, miny, w, h
ASPECT = VIEWBOX[2] / VIEWBOX[3]
MAX_GAUGE_W = 440

CHANNELS = [("Left",), ("Right",)]


def _clamp(v, a, b):
    return max(a, min(b, v))


def angle_for_level(level):
    t = (_clamp(level, VU_MIN, VU_MAX) - VU_MIN) / (VU_MAX - VU_MIN)
    return ANGLE_MIN - t * (ANGLE_MIN - ANGLE_MAX)


def gauge_point(r, deg):
    rad = math.radians(deg)
    x = PIVOT_X + r * math.cos(rad)
    y = PIVOT_Y - r * math.sin(rad)
    return (x, y)


class VUGauge(Widget):
    """A single needle gauge, drawn to exactly fill its own rect."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = -16.0
        self.peak = -10.0
        self._fit = None

        self._axis_labels = []
        for v in MAJOR_LEVELS:
            lbl = Label(
                text=str(v),
                font_name=theme.FONT_BODY,
                font_size=13,
                color=theme.NEUTRAL_400,
                size_hint=(None, None),
            )
            lbl.bind(texture_size=lambda w, ts: setattr(w, "size", ts))
            self._axis_labels.append((v, lbl))
            self.add_widget(lbl)

        self._db_label = Label(
            text="dB",
            font_name=theme.FONT_BODY,
            font_size=14,
            color=theme.with_alpha(theme.NEUTRAL_500, 0.6),
            size_hint=(None, None),
        )
        self._db_label.bind(texture_size=lambda w, ts: setattr(w, "size", ts))
        self.add_widget(self._db_label)

        self.bind(pos=self._on_geom, size=self._on_geom)

    def _on_geom(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        self._fit = ViewBoxFit(*VIEWBOX, self.x, self.y, self.width, self.height)
        self._layout_static()
        self._redraw()

    def _layout_static(self):
        fit = self._fit
        self.canvas.before.clear()
        with self.canvas.before:
            for v in MAJOR_LEVELS:
                angle = angle_for_level(v)
                outer = fit.pt(*gauge_point(122, angle))
                inner = fit.pt(*gauge_point(97, angle))
                Color(*theme.NEUTRAL_400)
                Line(points=[*outer, *inner], width=max(1.0, fit.length(1.5)))
            for v in MINOR_LEVELS:
                angle = angle_for_level(v)
                outer = fit.pt(*gauge_point(118, angle))
                inner = fit.pt(*gauge_point(104, angle))
                Color(*theme.NEUTRAL_600)
                Line(points=[*outer, *inner], width=max(1.0, fit.length(1.0)))

        for v, lbl in self._axis_labels:
            angle = angle_for_level(v)
            lx, ly = fit.pt(*gauge_point(137, angle))
            lbl.pos = (lx - lbl.width / 2, ly - lbl.height / 2)

        pivot_x, pivot_y = fit.pt(PIVOT_X, PIVOT_Y)
        db_x, db_y = fit.pt(PIVOT_X, 163)
        self._db_label.pos = (pivot_x - self._db_label.width / 2, db_y - self._db_label.height / 2)

    def set_values(self, level, peak):
        self.level = level
        self.peak = peak
        if self._fit:
            self._redraw()

    def _redraw(self):
        fit = self._fit
        self.canvas.after.clear()
        pivot = fit.pt(PIVOT_X, PIVOT_Y)
        needle_tip = fit.pt(*gauge_point(112, angle_for_level(self.level)))
        peak_pt = fit.pt(*gauge_point(118, angle_for_level(self.peak)))
        with self.canvas.after:
            Color(*theme.ACCENT_300)
            Line(points=[*pivot, *needle_tip], width=max(1.0, fit.length(2)), cap="round")
            Color(*theme.with_alpha(theme.ACCENT_300, 0.75))
            r = fit.length(2)
            Ellipse(pos=(peak_pt[0] - r, peak_pt[1] - r), size=(r * 2, r * 2))
            Color(*theme.NEUTRAL_300)
            r2 = fit.length(3)
            Ellipse(pos=(pivot[0] - r2, pivot[1] - r2), size=(r2 * 2, r2 * 2))


class VUChannelCell(Widget):
    """Centers a role label + gauge as one block, matching the source's
    flex column (align/justify: center) with a 440px gauge width cap."""

    def __init__(self, role_label, **kwargs):
        super().__init__(**kwargs)
        self._role_label = Label(
            text=role_label.upper(),
            font_name=theme.FONT_BODY,
            font_size=16,
            color=theme.with_alpha(theme.COLOR_TEXT, 0.45),
            size_hint=(None, None),
        )
        self._role_label.bind(texture_size=lambda w, ts: setattr(w, "size", ts))
        self.gauge = VUGauge(size_hint=(None, None))
        self.add_widget(self._role_label)
        self.add_widget(self.gauge)
        self.bind(pos=self._relayout, size=self._relayout)

    def _relayout(self, *args):
        avail_w, avail_h = self.width, self.height
        if avail_w <= 0 or avail_h <= 0:
            return
        gauge_w = min(avail_w, MAX_GAUGE_W)
        gauge_h = gauge_w / ASPECT
        gap = theme.SPACE_1
        label_h = self._role_label.height
        total_h = label_h + gap + gauge_h
        block_bottom = self.y + (avail_h - total_h) / 2
        cx = self.x + avail_w / 2

        top_y = block_bottom + total_h
        self._role_label.pos = (cx - self._role_label.width / 2, top_y - label_h)
        self.gauge.size = (gauge_w, gauge_h)
        self.gauge.pos = (cx - gauge_w / 2, block_bottom)

    def set_values(self, level, peak):
        self.gauge.set_values(level, peak)


class VUScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing=theme.SPACE_4, **kwargs)
        self.cells = [VUChannelCell("Left"), VUChannelCell("Right")]
        for cell in self.cells:
            self.add_widget(cell)

    def set_levels(self, levels, peaks):
        for cell, level, peak in zip(self.cells, levels, peaks):
            cell.set_values(level, peak)
