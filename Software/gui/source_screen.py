"""Source selector screen: a 4-column grid of input cards."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

import theme
from card import CardButton
from tag import Tag

SOURCE_DEFS = [
    {"id": "coax", "label": "Coaxial", "kicker": "Digital · S/PDIF"},
    {"id": "opt1", "label": "Optical 1", "kicker": "Digital · TOSLINK"},
    {"id": "opt2", "label": "Optical 2", "kicker": "Digital · TOSLINK"},
    {"id": "opt3", "label": "Optical 3", "kicker": "Digital · TOSLINK"},
    {"id": "usb", "label": "USB", "kicker": "Digital · Async"},
    {"id": "analog1", "label": "Analog 1", "kicker": "Line level · RCA"},
    {"id": "analog2", "label": "Analog 2", "kicker": "Line level · RCA"},
    {"id": "analog3", "label": "Analog 3", "kicker": "Line level · RCA"},
]

CARD_MIN_HEIGHT = 122
COLUMNS = 4


class SourceCard(CardButton):
    def __init__(self, source_id, label, kicker, on_press_cb, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1, None),
            height=CARD_MIN_HEIGHT,
            padding=(theme.SPACE_3, theme.SPACE_3, theme.SPACE_3, theme.SPACE_3),
            spacing=9,
            **kwargs,
        )
        self.source_id = source_id
        self._on_press_cb = on_press_cb

        self.kicker_label = Label(
            text=kicker.upper(),
            font_name=theme.FONT_BODY,
            font_size=14,
            color=theme.COLOR_ACCENT,
            size_hint=(1, None),
            halign="left",
            valign="middle",
        )
        self.kicker_label.bind(size=lambda w, v: setattr(w, "text_size", v))
        self.kicker_label.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1]))

        self.title_label = Label(
            text=label,
            font_name=theme.FONT_HEADING,
            font_size=25,
            color=theme.COLOR_TEXT,
            size_hint=(1, None),
            halign="left",
            valign="middle",
        )
        self.title_label.bind(size=lambda w, v: setattr(w, "text_size", v))
        self.title_label.bind(texture_size=lambda w, ts: setattr(w, "height", ts[1]))

        self.status_tag = Tag("—", variant="neutral", font_size=14, pad_h=10, pad_v=3)
        tag_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=self.status_tag.height)
        self.status_tag.bind(height=lambda w, v: setattr(tag_row, "height", v))
        tag_row.add_widget(self.status_tag)
        tag_row.add_widget(BoxLayout())  # push tag to the left (align-self: flex-start)

        self.add_widget(self.kicker_label)
        self.add_widget(self.title_label)
        self.add_widget(tag_row)

    def set_active(self, active):
        self.set_selected(active)
        self.status_tag.text = "Active" if active else "—"
        self.status_tag.set_variant("accent" if active else "neutral")

    def on_release(self):
        if self._on_press_cb:
            self._on_press_cb(self.source_id)


class SourceScreen(BoxLayout):
    def __init__(self, on_select, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self._on_select = on_select

        kicker = Label(
            text="SELECT INPUT",
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

        spacer = BoxLayout(size_hint=(1, None), height=theme.SPACE_3)
        self.add_widget(spacer)

        rows = (len(SOURCE_DEFS) + COLUMNS - 1) // COLUMNS
        grid_height = rows * CARD_MIN_HEIGHT + (rows - 1) * theme.SPACE_4
        grid = GridLayout(
            cols=COLUMNS,
            spacing=theme.SPACE_4,
            size_hint=(1, None),
            height=grid_height,
        )

        self.cards = {}
        for s in SOURCE_DEFS:
            card = SourceCard(s["id"], s["label"], s["kicker"], self._on_select)
            self.cards[s["id"]] = card
            grid.add_widget(card)

        self.add_widget(grid)
        self.add_widget(BoxLayout())  # remaining space stays empty, matches source content not filling column height

    def set_active_source(self, source_id):
        for sid, card in self.cards.items():
            card.set_active(sid == source_id)
