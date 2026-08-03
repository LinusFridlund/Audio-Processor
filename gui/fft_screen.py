"""Spectrum / FFT screen: a card containing a bar graph, ported from
the `fftGridLines` / `fftFreqLines` / `fftBars` computations in the
source `<script>` block."""

import math

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture

import theme
from svg_fit import ViewBoxFit

VIEWBOX = (0, 0, 1120, 380)
BAR_COUNT = 32
FREQ_MARKS = [(100, "100Hz"), (1000, "1kHz"), (10000, "10kHz")]
GRID_FRACTIONS = [0.0, 0.33, 0.66, 1.0]


def _freq_label_x(f):
    log_min, log_max = math.log10(20), math.log10(20000)
    return ((math.log10(f) - log_min) / (log_max - log_min)) * 1120


def _make_gradient_texture():
    """Vertical gradient accent-800 (bottom) -> accent (top), matching
    the SVG <linearGradient x1=0 y1=1 x2=0 y2=0>."""
    h = 256
    tex = Texture.create(size=(1, h), colorfmt="rgba")
    buf = bytearray(h * 4)
    c0, c1 = theme.ACCENT_800, theme.COLOR_ACCENT
    for row in range(h):
        t = row / (h - 1)
        r = c0[0] + (c1[0] - c0[0]) * t
        g = c0[1] + (c1[1] - c0[1]) * t
        b = c0[2] + (c1[2] - c0[2]) * t
        buf[row * 4 + 0] = int(r * 255)
        buf[row * 4 + 1] = int(g * 255)
        buf[row * 4 + 2] = int(b * 255)
        buf[row * 4 + 3] = 255
    tex.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
    tex.wrap = "clamp_to_edge"
    return tex


_GRADIENT_TEXTURE = None


def gradient_texture():
    global _GRADIENT_TEXTURE
    if _GRADIENT_TEXTURE is None:
        _GRADIENT_TEXTURE = _make_gradient_texture()
    return _GRADIENT_TEXTURE


class FFTGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bars = [0.0] * BAR_COUNT
        self.peaks = [0.2] * BAR_COUNT
        self._fit = None

        self._freq_labels = []
        for f, text in FREQ_MARKS:
            lbl = Label(
                text=text,
                font_name=theme.FONT_BODY,
                font_size=17,
                color=theme.NEUTRAL_400,
                size_hint=(None, None),
            )
            lbl.bind(texture_size=lambda w, ts: setattr(w, "size", ts))
            self._freq_labels.append((f, lbl))
            self.add_widget(lbl)

        self.bind(pos=self._on_geom, size=self._on_geom)

    def _on_geom(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        self._fit = ViewBoxFit(*VIEWBOX, self.x, self.y, self.width, self.height)
        self._layout_static()
        self._redraw_bars()

    def _layout_static(self):
        fit = self._fit
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*theme.NEUTRAL_800)
            for frac in GRID_FRACTIONS:
                y = 20 + frac * 320
                p1, p2 = fit.pt(0, y), fit.pt(1120, y)
                Line(points=[*p1, *p2], width=max(1.0, fit.length(1)), dash_length=fit.length(2), dash_offset=fit.length(3))
            for f, _ in FREQ_MARKS:
                x = _freq_label_x(f)
                p1, p2 = fit.pt(x, 0), fit.pt(x, 340)
                Line(points=[*p1, *p2], width=max(1.0, fit.length(1)))

        for f, lbl in self._freq_labels:
            x = _freq_label_x(f)
            lx, ly = fit.pt(x, 362)
            lbl.pos = (lx - lbl.width / 2, ly - lbl.height / 2)

    def set_values(self, bars, peaks):
        self.bars = bars
        self.peaks = peaks
        if self._fit:
            self._redraw_bars()

    def _redraw_bars(self):
        fit = self._fit
        self.canvas.after.clear()
        bar_w = 1120 / BAR_COUNT
        tex = gradient_texture()
        radius = max(0.5, fit.length(1.5))
        with self.canvas.after:
            for i in range(BAR_COUNT):
                v = self.bars[i] if i < len(self.bars) else 0.0
                pk = self.peaks[i] if i < len(self.peaks) else 0.0
                x = i * bar_w + bar_w * 0.15
                w = bar_w * 0.7
                h = v * 320
                y = 340 - h
                p0 = fit.pt(x, y + h)  # bottom-left of bar (svg y grows down, kivy needs bottom = higher svg y)
                p1 = fit.pt(x + w, y)  # top-right
                rx0, ry0 = min(p0[0], p1[0]), min(p0[1], p1[1])
                rw, rh = abs(p1[0] - p0[0]), abs(p1[1] - p0[1])
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=(rx0, ry0), size=(rw, max(rh, 0.0001)), radius=[radius], texture=tex)

                peak_y = 340 - pk * 320 - 2
                pp0 = fit.pt(x, peak_y + 2)
                pp1 = fit.pt(x + w, peak_y)
                prx0, pry0 = min(pp0[0], pp1[0]), min(pp0[1], pp1[1])
                prw, prh = abs(pp1[0] - pp0[0]), abs(pp1[1] - pp0[1])
                Color(*theme.ACCENT_300)
                Rectangle(pos=(prx0, pry0), size=(prw, prh))


class FFTScreen(BoxLayout):
    """The `.card` wrapper: kicker/label header row, then the graph."""

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=(theme.SPACE_4, theme.SPACE_4, theme.SPACE_4, theme.SPACE_4),
            spacing=theme.SPACE_2 * 2,  # flex `gap` + the header row's own margin-bottom
            **kwargs,
        )
        from kivy.graphics import RoundedRectangle as _RR

        with self.canvas.before:
            Color(*theme.COLOR_SURFACE)
            self._bg = _RR(pos=self.pos, size=self.size, radius=[theme.RADIUS_MD])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=22)
        self.kicker = Label(
            text="",
            font_name=theme.FONT_BODY,
            font_size=16,
            color=theme.COLOR_ACCENT,
            halign="left",
            valign="middle",
        )
        self.kicker.bind(size=lambda w, v: setattr(w, "text_size", v))
        self.info = Label(
            text="dBFS · 20Hz–20kHz",
            font_name=theme.FONT_BODY,
            font_size=14,
            color=theme.with_alpha(theme.COLOR_TEXT, 0.5),
            halign="right",
            valign="middle",
        )
        self.info.bind(size=lambda w, v: setattr(w, "text_size", v))
        header.add_widget(self.kicker)
        header.add_widget(self.info)
        self.add_widget(header)

        self.graph = FFTGraph(size_hint=(1, 1))
        self.add_widget(self.graph)

    def _sync_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def set_source_label(self, label):
        self.kicker.text = f"SPECTRUM · {label.upper()}"

    def set_values(self, bars, peaks):
        self.graph.set_values(bars, peaks)
