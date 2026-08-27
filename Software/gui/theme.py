"""Design tokens ported from the Nocturne design system
(_ds/nocturne-.../styles.css) used by the Claude Design prototype.

Colors are stored as Kivy-style RGBA float tuples (0..1). Where the
source CSS used `color-mix(... transparent)` to get a translucent
color, that's reproduced here as an RGBA tuple with alpha < 1.
"""

import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _hex(h, a=1.0):
    h = h.lstrip("#")
    r = int(h[0:2], 16) / 255
    g = int(h[2:4], 16) / 255
    b = int(h[4:6], 16) / 255
    return (r, g, b, a)


# --- base -------------------------------------------------------------
COLOR_BG = _hex("#161826")
COLOR_SURFACE = _hex("#232532")
COLOR_TEXT = _hex("#e9e9ed")
COLOR_ACCENT = _hex("#9184d9")
COLOR_ACCENT_2 = _hex("#a7a1db")
COLOR_DIVIDER = _hex("#e9e9ed", 0.16)

# --- neutral ramp -------------------------------------------------------
NEUTRAL_100 = _hex("#f3f5fe")
NEUTRAL_200 = _hex("#e4e7f5")
NEUTRAL_300 = _hex("#cfd3e5")
NEUTRAL_400 = _hex("#b2b6ca")
NEUTRAL_500 = _hex("#9397ab")
NEUTRAL_600 = _hex("#75798c")
NEUTRAL_700 = _hex("#595d6c")
NEUTRAL_800 = _hex("#3f424d")
NEUTRAL_900 = _hex("#292b31")

# --- accent ramp ----------------------------------------------------------
ACCENT_100 = _hex("#f5f4ff")
ACCENT_200 = _hex("#e7e5fe")
ACCENT_300 = _hex("#d2cefd")
ACCENT_400 = _hex("#b5abfc")
ACCENT_500 = _hex("#968ae0")
ACCENT_600 = _hex("#796cbf")
ACCENT_700 = _hex("#5d5294")
ACCENT_800 = _hex("#423a6a")
ACCENT_900 = _hex("#2b2741")


def with_alpha(color, alpha):
    return (color[0], color[1], color[2], alpha)


# --- spacing scale --------------------------------------------------------
# styles.css defines --space-1..4,6,8 as N * 2.8px (skipping 5 and 7,
# which the .dc.html nonetheless references) — the ramp is linear, so
# the missing steps are filled in with the same formula.
def space(n):
    return round(n * 2.8, 2)


SPACE_1 = space(1)
SPACE_2 = space(2)
SPACE_3 = space(3)
SPACE_4 = space(4)
SPACE_5 = space(5)
SPACE_6 = space(6)
SPACE_8 = space(8)

# --- radii ------------------------------------------------------------
RADIUS_SM = 4
RADIUS_MD = 8
RADIUS_LG = 14

# --- fonts ------------------------------------------------------------
FONT_REGULAR = os.path.join(_HERE, "assets/fonts/Inter-Regular.ttf")
FONT_MEDIUM = os.path.join(_HERE, "assets/fonts/Inter-Medium.ttf")
FONT_SEMIBOLD = os.path.join(_HERE, "assets/fonts/Inter-SemiBold.ttf")
FONT_BOLD = os.path.join(_HERE, "assets/fonts/Inter-Bold.ttf")

FONT_BODY = FONT_REGULAR
FONT_HEADING = FONT_MEDIUM  # --font-heading-weight: 500
