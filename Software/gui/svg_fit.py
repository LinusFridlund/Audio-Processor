"""Maps coordinates from an SVG viewBox's coordinate space (origin
top-left, y grows downward) onto a Kivy widget's pixel rect (origin
bottom-left, y grows upward), preserving aspect ratio the way SVG's
default `preserveAspectRatio="xMidYMid meet"` does: scale uniformly to
fit, then center on whichever axis has slack.
"""


class ViewBoxFit:
    def __init__(self, minx, miny, vw, vh, x, y, w, h):
        self.minx = minx
        self.miny = miny
        self.vh = vh
        self.scale = min(w / vw, h / vh) if vw and vh else 1.0
        rendered_w = vw * self.scale
        rendered_h = vh * self.scale
        self.offset_x = x + (w - rendered_w) / 2
        self.offset_y = y + (h - rendered_h) / 2

    def pt(self, vx, vy):
        px = self.offset_x + (vx - self.minx) * self.scale
        py = self.offset_y + (self.vh - (vy - self.miny)) * self.scale
        return (px, py)

    def length(self, l):
        return l * self.scale


class ViewBoxStretch:
    """Non-uniform fit (viewBox stretched independently on each axis).
    Used only where the SVG's rendered box has (almost) the same aspect
    ratio as its viewBox, so uniform vs. stretched fit are visually
    indistinguishable."""

    def __init__(self, minx, miny, vw, vh, x, y, w, h):
        self.minx = minx
        self.miny = miny
        self.vh = vh
        self.sx = w / vw if vw else 1.0
        self.sy = h / vh if vh else 1.0
        self.offset_x = x
        self.offset_y = y

    def pt(self, vx, vy):
        px = self.offset_x + (vx - self.minx) * self.sx
        py = self.offset_y + (self.vh - (vy - self.miny)) * self.sy
        return (px, py)
