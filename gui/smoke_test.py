"""Dev-only helper: launches the app, cycles through all 4 screens,
and dumps a screenshot of each — used to visually verify the layout
against the design without a physical device."""

import os

os.environ["DEVICE_DISPLAY_WINDOWED"] = "1"

from main import DeviceDisplayApp  # noqa: E402  (sets window Config before Window is created)

from kivy.clock import Clock
from kivy.core.window import Window

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
SCREENS = ["vu", "fft", "source", "peq"]


def run():
    os.makedirs(OUT_DIR, exist_ok=True)
    app = DeviceDisplayApp()

    def sequence(dt, i=[0]):
        idx = i[0]
        if idx > 0:
            Window.screenshot(name=os.path.join(OUT_DIR, f"shot_{SCREENS[idx - 1]}.png"))
        if idx < len(SCREENS):
            app.set_screen(SCREENS[idx])
            i[0] += 1
            Clock.schedule_once(sequence, 0.6)
        else:
            Clock.schedule_once(lambda dt: app.stop(), 0.3)

    Clock.schedule_once(sequence, 0.8)
    app.run()


if __name__ == "__main__":
    run()
