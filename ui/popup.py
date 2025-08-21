from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from ui.theme import (
    POPUP_HEIGHT, COLOR_BACKGROUND, COLOR_PROGRESS, COLOR_SAFE, COLOR_UNSAFE,
    COLOR_UNKNOWN, COLOR_TEXT, COLOR_TEXT_ACTION, ANIMATION_DURATION_FILL,
    ANIMATION_DURATION_FADEOUT, AUTO_DISMISS_DURATION
)

class BottomProgressPopup(ModalView):
    progress = NumericProperty(0.0)
    message = StringProperty("Initializing...")
    fill_color = ListProperty(COLOR_PROGRESS)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = dp(POPUP_HEIGHT)
        self.pos_hint = {'bottom': 1}
        self.background_color = [0, 0, 0, 0]
        self.auto_dismiss = False

        with self.canvas.before: # type: ignore
            Color(*COLOR_BACKGROUND)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
            Color(*self.fill_color)
            self.fill_rect = Rectangle(size=(0, self.height), pos=self.pos)

        self.label = Label(
            text=self.message,
            font_size=dp(16),
            color=COLOR_TEXT
        )
        self.add_widget(self.label)

        self.action_button = Button(
            text="",
            size_hint=(None, None),
            size=(dp(120), self.height),
            pos_hint={'right': 1},
            background_color=[0,0,0,0],
            font_size=dp(14),
            color=COLOR_TEXT_ACTION,
            opacity=0
        )
        self.add_widget(self.action_button)

        self.bind(size=self._update_graphics, pos=self._update_graphics) # type: ignore
        self.bind(progress=self._update_progress) # type: ignore
        self.bind(message=self._update_message) # type: ignore
        self.bind(fill_color=self._update_fill_color) # type: ignore

    def _update_graphics(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.fill_rect.pos = self.pos
        self.fill_rect.size = (self.width * self.progress, self.height)
        self.action_button.size = (dp(120), self.height)

    def _update_progress(self, instance, value):
        target_width = self.width * value
        anim = Animation(size=(target_width, self.height), duration=ANIMATION_DURATION_FILL)
        anim.start(self.fill_rect)

    def _update_message(self, instance, value):
        self.label.text = value

    def _update_fill_color(self, instance, value):
        # Animate color transition
        anim = Animation(rgba=value, duration=ANIMATION_DURATION_FILL)
        # To animate a canvas color, we need to create a new Color instruction
        # For simplicity, we'll just set it directly for now.
        self.canvas.before.remove(self.fill_rect) # type: ignore
        with self.canvas.before: # type: ignore
            Color(*value)
            self.fill_rect = Rectangle(
                size=(self.width * self.progress, self.height),
                pos=self.pos
            )

    def show(self, progress, message):
        self.progress = progress
        self.message = message
        self.open()

    def update_state(self, progress, message, *args):
        self.progress = progress
        self.message = message

    def complete(self, verdict_label, final_url, open_callback, copy_callback):
        self.progress = 1.0
        self.message = verdict_label.upper()
        self.action_button.opacity = 1

        if verdict_label == "SAFE":
            self.fill_color = COLOR_SAFE
            self.action_button.text = "Open"
            self.action_button.on_press = lambda: open_callback(final_url)
        elif verdict_label in ["UNSAFE", "SUSPICIOUS"]:
            self.fill_color = COLOR_UNSAFE
            self.action_button.text = "Open anyway"
            self.action_button.on_press = lambda: open_callback(final_url)
        else: # UNKNOWN
            self.fill_color = COLOR_UNKNOWN
            self.message = "UNKNOWN"
            self.action_button.text = "Copy URL"
            self.action_button.on_press = lambda: copy_callback(final_url)

        Clock.schedule_once(self.fade_out_dismiss, AUTO_DISMISS_DURATION)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.fade_out_dismiss()
            return True
        return super().on_touch_down(touch)

    def fade_out_dismiss(self, *args):
        anim = Animation(opacity=0, duration=ANIMATION_DURATION_FADEOUT)
        anim.bind(on_complete=lambda *x: self.dismiss())
        anim.start(self)
