"""Line-icon widget that redraws the inline SVGs from the sidebar as
Kivy canvas instructions. Every icon lives in a 24x24 viewBox (matching
the source `viewBox="0 0 24 24"`), stroke-width 2, round caps/joins —
copied straight from `Device Display.dc.html`.

Ops:
  ('line', x1, y1, x2, y2)
  ('polyline', [(x, y), ...])
  ('dot', cx, cy, r)          filled circle
  ('ring', cx, cy, r)         stroked circle (no fill)
  ('top_arc', cx, cy, r)      top half of a circle (the VU gauge arc)
"""

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse

ICONS = {
    "vu": [
        ("top_arc", 12, 18, 8),
        ("line", 12, 18, 16, 11),
        ("dot", 12, 18, 1.5),
    ],
    "spectrum": [
        ("line", 5, 19, 5, 10),
        ("line", 10, 19, 10, 5),
        ("line", 15, 19, 15, 13),
        ("line", 20, 19, 20, 8),
    ],
    "source": [
        ("line", 4, 12, 14, 12),
        ("polyline", [(10, 7), (15, 12), (10, 17)]),
        ("line", 17, 5, 17, 19),
    ],
    "peq": [
        ("line", 6, 4, 6, 20),
        ("dot", 6, 9, 2),
        ("line", 12, 4, 12, 20),
        ("dot", 12, 15, 2),
        ("line", 18, 4, 18, 20),
        ("dot", 18, 7, 2),
    ],
    "encoder": [
        ("ring", 12, 12, 9),
        ("line", 12, 12, 12, 6),
    ],
}

VIEWBOX = 24.0


class IconWidget(Widget):
    def __init__(self, icon, color=(1, 1, 1, 1), **kwargs):
        self.icon = icon
        self.icon_color = color
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def set_color(self, color):
        self.icon_color = color
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        ops = ICONS.get(self.icon, [])
        if self.width <= 0 or self.height <= 0:
            return
        scale = min(self.width, self.height) / VIEWBOX
        stroke = max(1.0, 2 * scale)

        def pt(vx, vy):
            # svg y-down -> kivy y-up, centered in the widget's box
            return (self.x + vx * scale, self.y + (VIEWBOX - vy) * scale)

        with self.canvas:
            Color(*self.icon_color)
            for op in ops:
                kind = op[0]
                if kind == "line":
                    _, x1, y1, x2, y2 = op
                    p1, p2 = pt(x1, y1), pt(x2, y2)
                    Line(points=[*p1, *p2], width=stroke, cap="round")
                elif kind == "polyline":
                    _, pts = op
                    flat = []
                    for vx, vy in pts:
                        flat.extend(pt(vx, vy))
                    Line(points=flat, width=stroke, cap="round", joint="round")
                elif kind == "dot":
                    _, cx, cy, r = op
                    cpt = pt(cx, cy)
                    rr = r * scale
                    Ellipse(pos=(cpt[0] - rr, cpt[1] - rr), size=(rr * 2, rr * 2))
                elif kind == "ring":
                    _, cx, cy, r = op
                    cpt = pt(cx, cy)
                    rr = r * scale
                    Line(
                        ellipse=(cpt[0] - rr, cpt[1] - rr, rr * 2, rr * 2),
                        width=stroke,
                    )
                elif kind == "top_arc":
                    _, cx, cy, r = op
                    cpt = pt(cx, cy)
                    rr = r * scale
                    # Kivy's ellipse angles run clockwise from north (0=N, 90=E,
                    # 180=S, 270=W) — West(-90) through North(0) to East(90)
                    # traces the top half.
                    Line(
                        ellipse=(cpt[0] - rr, cpt[1] - rr, rr * 2, rr * 2, -90, 90),
                        width=stroke,
                        cap="round",
                    )
