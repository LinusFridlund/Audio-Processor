# Device Display

Kivy port of the `Device Display.dc.html` Claude Design prototype: the
on-device touchscreen UI for a home audio processor (VU meters, FFT
spectrum, source selector, PEQ presets), built for a 1280x720 5" panel
on a Raspberry Pi 5.

The audio data (VU levels, spectrum bars) is simulated with the same
random-walk the original prototype used, so the display runs and looks
right standalone. Swap `DeviceDisplayApp._retarget` / `_tick` in
`main.py` for real reads once you have a DSP/DAC interface to pull
from — everything downstream (gauges, bars) just consumes plain
Python lists of levels, no other code needs to change.

## Layout

```
main.py            App, screen switching, simulated data timers
theme.py           Colors/spacing/fonts ported from the design system
svg_fit.py          viewBox-style aspect-fit math shared by the gauges
icons.py             Sidebar line icons, drawn on canvas (no image assets)
card.py               The reusable ".card" surface + selected-ring style
tag.py                 Small rounded status chip
sidebar.py              Left nav rail
header.py                Title + status chips bar
vu_screen.py              VU meter gauges
fft_screen.py              Spectrum bar graph
source_screen.py            Source picker grid
peq_screen.py                 PEQ preset list + mini response curves
assets/fonts/                 Inter (the design's font), bundled as static weights
smoke_test.py                 Dev helper: screenshots all 4 screens (see below)
```

## Running on the Raspberry Pi 5

1. **System packages** (Raspberry Pi OS, Bookworm or newer):

   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip \
       libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libmtdev1 libgl1-mesa-dri
   ```

2. **Install into a virtualenv:**

   ```bash
   cd device_display
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run it:**

   ```bash
   python3 main.py
   ```

   By default it launches fullscreen at your display's native
   resolution (`Config.set('graphics', 'fullscreen', 'auto')`) with the
   mouse cursor hidden — meant for a touchscreen with nothing else on
   it. For windowed testing on a desktop (or over VNC), run instead:

   ```bash
   DEVICE_DISPLAY_WINDOWED=1 python3 main.py
   ```

### Touchscreen input

Kivy auto-detects the touch panel through the kernel's `evdev`/`hid`
input layer on Raspberry Pi OS — no extra config needed for most
official/HDMI touch panels. If touches aren't registering or are
mis-calibrated, check `~/.kivy/config.ini`'s `[input]` section, or set
an explicit provider, e.g.:

```ini
[input]
mtdev_%(name)s = probesysfs,provider=mtdev
```

(`xinput_calibrator` or `libinput` calibration matrices apply as usual
for panels needing it — that's independent of this app.)

### Autostart on boot (kiosk mode)

Add a systemd user service so it comes up after login without a
desktop shell:

```ini
# ~/.config/systemd/user/device-display.service
[Unit]
Description=Device Display
After=graphical-session.target

[Service]
ExecStart=/home/pi/device_display/.venv/bin/python3 /home/pi/device_display/main.py
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=graphical-session.target
```

```bash
systemctl --user enable --now device-display.service
```

Also worth doing on a dedicated kiosk display:
- Disable screen blanking/DPMS (`xset s off; xset -dpms` in whatever
  starts your X/Wayland session, or the equivalent compositor setting).
- Boot straight to the display manager's auto-login so the service's
  `graphical-session.target` is reached without a login prompt.

## Verifying changes without hardware

`smoke_test.py` launches the app, cycles through all four screens, and
saves a screenshot of each — useful for checking layout after edits
without a Pi or physical screen attached:

```bash
DEVICE_DISPLAY_WINDOWED=1 python3 smoke_test.py
```

(On a headless machine, run it under `xvfb-run -s "-screen 0
1280x720x24"`.) Screenshots land in `device_display/screenshots/`.

## Notes on fidelity to the prototype

- Colors, spacing, radii, and font sizes are copied directly from the
  design's `_ds/nocturne-.../styles.css` tokens and the inline styles
  in `Device Display.dc.html` — including the two spacing steps
  (`--space-5`, `--space-7`) that file uses but the token sheet never
  defines; those are filled in by extending the sheet's own `2.8px *
  N` progression.
- The PEQ preset rows reproduce the source's literal `flex-direction:
  row; justify-content: space-between` behavior across its 3 children
  (name, status tag, curve) — including the fact that the tag lands
  wherever the space-between math puts it, not glued to the name.
  That's what the shipped prototype does, so that's what's here.
- The outer 14px `border-radius` on the prototype's root `<div>` (a
  stand-in "device frame" in the browser mockup) is intentionally
  dropped — on real hardware this app *is* the whole physical screen,
  so there's no frame to round against.
- `needleGlow` and `fftBarCount` were exposed as tunable props in the
  Claude Design prototype; this port hardcodes their shipped defaults
  (glow off, 32 bars) since there's no design-tool inspector here to
  tune them live. Change `BAR_COUNT` in `fft_screen.py` or add the
  glow's `filter`-equivalent (a soft blurred line under the needle) in
  `vu_screen.py` if you want them back.
