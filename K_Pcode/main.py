from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from datetime import datetime, timedelta

Window.size = (300, 510)

KV = """
ControlPanel:
    orientation: "vertical"
    padding: "40dp"
    spacing: "40dp"

    # --- AC Status ---
    MDLabel:
        id: status_label
        text: "AC is OFF"
        halign: "center"
        theme_text_color: "Error"
        font_style: "H5"

    # --- Power Button ---
    MDFillRoundFlatIconButton:
        text: "Power"
        icon: "power"
        pos_hint: {"center_x": 0.5}
        on_release: root.toggle_ac()

    # --- Temperature ---
    MDLabel:
        id: temp_label
        text: "24°C"
        halign: "center"
        font_style: "H4"

    BoxLayout:
        size_hint_y: None
        height: "80dp"
        spacing: "30dp"
        MDFillRoundFlatIconButton:
            text: "Temp "
            icon: "minus"
            on_release: root.decrease_temp()
        MDFillRoundFlatIconButton:
            text: "Temp "
            icon: "plus"
            on_release: root.increase_temp()

    # --- Timer Input ---
    MDTextField:
        id: timer_input
        hint_text: "Minutes (1-60)"
        helper_text_mode: "on_focus"
        size_hint_x: 1
        mode: "rectangle"

    # --- Set Timer Button ---
    MDFillRoundFlatIconButton:
        text: "Set Timer"
        icon: "timer"
        pos_hint: {"center_x": 0.5}
        on_release: root.set_timer()

    # --- Timer Status ---
    MDLabel:
        id: timer_label
        text: "Time: --:--"
        halign: "center"
        font_style: "Subtitle1"
"""

class ControlPanel(MDBoxLayout):
    ac_on = BooleanProperty(False)
    temperature = NumericProperty(24)
    timer_end = StringProperty("--:--")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_timer, 1)

    def toggle_ac(self):
        self.ac_on = not self.ac_on
        if self.ac_on:
            self.ids.status_label.text = "AC is ON"
            self.ids.status_label.theme_text_color = "Custom"
            self.ids.status_label.text_color = (0, 1, 0, 1)  # green
        else:
            self.ids.status_label.text = "AC is OFF"
            self.ids.status_label.theme_text_color = "Error"

    def increase_temp(self):
        self.temperature += 1
        self.ids.temp_label.text = f"{self.temperature}°C"

    def decrease_temp(self):
        self.temperature -= 1
        self.ids.temp_label.text = f"{self.temperature}°C"

    def set_timer(self):
        try:
            minutes = int(self.ids.timer_input.text)
            if minutes <= 0:
                raise ValueError
            end_time = datetime.now() + timedelta(minutes=minutes)
            self.timer_end = end_time.strftime("%H:%M:%S")
            self.ids.timer_label.text = f"Timer until: {self.timer_end}"
        except ValueError:
            self.ids.timer_label.text = "Invalid minutes!"

    def update_timer(self, dt):
        if self.timer_end != "--:--":
            try:
                end_time = datetime.strptime(self.timer_end, "%H:%M:%S")
                now = datetime.now().strftime("%H:%M:%S")
                if now >= self.timer_end:
                    self.ac_on = False
                    self.toggle_ac()
                    self.timer_end = "--:--"
                    self.ids.timer_label.text = "Timer expired"
            except Exception:
                pass
            

class ACRemoteApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string(KV)

if __name__ == "__main__":
    ACRemoteApp().run()
