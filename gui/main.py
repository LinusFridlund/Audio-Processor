"""Device display for a Raspberry Pi based home audio processor.

Recreates `Device Display.dc.html` (a Claude Design prototype) as a
native Kivy app: a 1280x720 touchscreen UI with VU meters, an FFT
spectrum view, a source selector, and PEQ preset picker.

The prototype's audio data (VU levels, spectrum bars) was randomly
simulated in JS — this keeps the same simulation so the display runs
standalone. Swap `_retarget`/`_tick` below for real reads from your DSP
once that interface exists.
"""

import os
import random

from kivy.config import Config

WINDOWED = os.environ.get("DEVICE_DISPLAY_WINDOWED") == "1"
Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "720")
Config.set("graphics", "resizable", "0")
if not WINDOWED:
    Config.set("graphics", "fullscreen", "auto")
    Config.set("graphics", "show_cursor", "0")
# Stops a mouse right-click from spawning a simulated second touch point
# (Kivy's default "red dot" multitouch emulation) — irrelevant to the
# touchscreen itself, but avoids surprises when testing with a mouse.
Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

import theme
from sidebar import Sidebar
from header import Header
from vu_screen import VUScreen, VU_MIN, VU_MAX
from fft_screen import FFTScreen, BAR_COUNT
from source_screen import SourceScreen, SOURCE_DEFS
from peq_screen import PEQScreen, PRESET_DEFS

TITLES = {"vu": "VU Meters", "fft": "Spectrum", "source": "Source", "peq": "PEQ Presets"}
AUDIO_FORMAT_LABEL = "96kHz / 24-bit"
FFT_STATE_LEN = 48


def _clamp(v, a, b):
    return max(a, min(b, v))


class ContentArea(BoxLayout):
    """The flex:1 content pane — insets by --space-5 and shows exactly
    one screen at a time."""

    def __init__(self, **kwargs):
        super().__init__(
            padding=(theme.SPACE_5, theme.SPACE_5, theme.SPACE_5, theme.SPACE_5),
            **kwargs,
        )

    def show(self, widget):
        self.clear_widgets()
        self.add_widget(widget)


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", size=(1280, 720), size_hint=(None, None), **kwargs)
        with self.canvas.before:
            Color(*theme.COLOR_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_bg, size=self._sync_bg)

    def _sync_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class DeviceDisplayApp(App):
    def build(self):
        self.title = "Device Display"

        self.screen = "vu"
        self.active_source = "coax"
        self.active_preset = "default"

        self.vu_levels = [-16.0, -12.0]
        self.vu_peaks = [-10.0, -8.0]
        self._vu_targets = list(self.vu_levels)

        self.fft_bars = [random.random() * 0.4 for _ in range(FFT_STATE_LEN)]
        self.fft_peaks = [0.2] * FFT_STATE_LEN
        self._fft_targets = [random.random() * 0.9 for _ in range(FFT_STATE_LEN)]

        self.root_widget = RootWidget()
        self.sidebar = Sidebar(on_select=self.set_screen)
        self.header = Header()

        right_col = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.content_area = ContentArea(size_hint=(1, 1))
        right_col.add_widget(self.header)
        right_col.add_widget(self.content_area)

        self.root_widget.add_widget(self.sidebar)
        self.root_widget.add_widget(right_col)

        self.screens = {
            "vu": VUScreen(),
            "fft": FFTScreen(),
            "source": SourceScreen(on_select=self.set_source),
            "peq": PEQScreen(on_select=self.set_preset),
        }
        self.screens["source"].set_active_source(self.active_source)
        self.screens["peq"].set_active_preset(self.active_preset)

        self.set_screen(self.screen)

        Clock.schedule_interval(self._retarget, 1.3)
        Clock.schedule_interval(self._tick, 0.07)

        return self.root_widget

    def set_screen(self, screen_id):
        self.screen = screen_id
        self.sidebar.set_active_screen(screen_id)
        self.content_area.show(self.screens[screen_id])
        self._update_header()

    def set_source(self, source_id):
        self.active_source = source_id
        self.screens["source"].set_active_source(source_id)
        self._update_header()

    def set_preset(self, preset_id):
        self.active_preset = preset_id
        self.screens["peq"].set_active_preset(preset_id)
        self._update_header()

    def _update_header(self):
        source_def = next((s for s in SOURCE_DEFS if s["id"] == self.active_source), None)
        preset_def = next((p for p in PRESET_DEFS if p["id"] == self.active_preset), None)
        self.header.set_values(
            TITLES[self.screen],
            source_def["label"] if source_def else "",
            AUDIO_FORMAT_LABEL,
            preset_def["name"] if preset_def else "",
        )
        self.screens["fft"].set_source_label(source_def["label"] if source_def else "")

    def _retarget(self, dt):
        self._vu_targets = [VU_MIN + random.random() * (VU_MAX - VU_MIN) for _ in self._vu_targets]
        self._fft_targets = [
            _clamp(max(0.0, 0.85 - i * 0.014) * (0.3 + random.random() * 0.9), 0.0, 1.0)
            for i in range(FFT_STATE_LEN)
        ]

    def _tick(self, dt):
        self.vu_levels = [
            v + (_clamp(t, VU_MIN, VU_MAX) - v) * 0.16 for v, t in zip(self.vu_levels, self._vu_targets)
        ]
        self.vu_peaks = [max(v, p - 0.25) for v, p in zip(self.vu_levels, self.vu_peaks)]
        self.fft_bars = [v + (t - v) * 0.22 for v, t in zip(self.fft_bars, self._fft_targets)]
        self.fft_peaks = [max(v, p - 0.015) for v, p in zip(self.fft_bars, self.fft_peaks)]

        self.screens["vu"].set_levels(self.vu_levels, self.vu_peaks)
        self.screens["fft"].set_values(self.fft_bars[:BAR_COUNT], self.fft_peaks[:BAR_COUNT])


if __name__ == "__main__":
    DeviceDisplayApp().run()
