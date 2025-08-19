from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
import requests


# --- MockAPI Service ---
class MockAPIService:
    def __init__(self):
        self.base_url = "https://68947b91be3700414e135ca5.mockapi.io/tele/1"

    def update_onoff(self, value):
        self.send_data({"on_off": value})

    def update_temperature(self, temp):
        self.send_data({"temperature": temp})

    def update_timer(self, time_str):
        self.send_data({"timer": time_str})

    def send_data(self, data):
        try:
            response = requests.put(self.base_url, json=data)
            print("✅ Updated:", response.json())
        except Exception as e:
            print("❌ Error sending to API:", e)


# --- ON/OFF Control ---
class OnOffControl(BoxLayout):
    def __init__(self, api_service, **kwargs):
        super().__init__(**kwargs)
        self.api = api_service
        self.orientation = 'vertical'
        self.spacing = 10

        self.status_label = Label(text="AC is OFF", font_size=30, color=(1, 0, 0, 1))
        self.add_widget(self.status_label)

        toggle_button = Button(text="OFF/ON", size_hint=(1, 0.5), background_color=(0.3, 0, 0.3, 1))
        toggle_button.bind(on_press=self.toggle_ac)
        self.add_widget(toggle_button)

    def toggle_ac(self, instance=None):
        if self.status_label.text == "AC is OFF":
            self.status_label.text = "AC is ON"
            self.status_label.color = (0, 1, 0, 1)
            self.api.update_onoff(1)
        else:
            self.status_label.text = "AC is OFF"
            self.status_label.color = (1, 0, 0, 1)
            self.api.update_onoff(0)

    def turn_off(self):
        self.status_label.text = "AC is OFF"
        self.status_label.color = (1, 0, 0, 1)
        self.api.update_onoff(0)


# --- Temperature Control ---
class TemperatureControl(BoxLayout):
    def __init__(self, api_service, **kwargs):
        super().__init__(**kwargs)
        self.api = api_service
        self.orientation = 'vertical'
        self.spacing = 10

        self.min_temp = 16
        self.max_temp = 30
        self.temp = 16

        self.temp_label = Label(text=f"{self.temp}°C", font_size=55, color=(0, 0, 0, 1))
        self.add_widget(self.temp_label)

        temp_buttons = BoxLayout(spacing=35)
        minus_btn = Button(text="-", background_color=(0.5, 0, 0, 1))
        minus_btn.bind(on_press=self.decrease_temp)
        plus_btn = Button(text="+", background_color=(0.3, 0.3, 0.3, 1))
        plus_btn.bind(on_press=self.increase_temp)
        temp_buttons.add_widget(minus_btn)
        temp_buttons.add_widget(plus_btn)
        self.add_widget(temp_buttons)

    def increase_temp(self, instance):
        if self.temp < self.max_temp:
            self.temp += 1
            self.temp_label.text = f"{self.temp}°C"
            self.api.update_temperature(self.temp)

    def decrease_temp(self, instance):
        if self.temp > self.min_temp:
            self.temp -= 1
            self.temp_label.text = f"{self.temp}°C"
            self.api.update_temperature(self.temp)


# --- Timer Control ---
class TimerControl(BoxLayout):
    def __init__(self, api_service, onoff_control, **kwargs):
        super().__init__(**kwargs)
        self.api = api_service
        self.onoff_control = onoff_control
        self.remaining_seconds = 0
        self.timer_event = None
        self.orientation = 'vertical'
        self.spacing = 15
        self.padding = [10, 10, 10, 10]

        input_box = BoxLayout(size_hint=(1, 0.6), padding=5)
        with input_box.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.bg_rect = RoundedRectangle(radius=[10], pos=input_box.pos, size=input_box.size)
        input_box.bind(pos=self.update_bg, size=self.update_bg)

        self.timer_input = TextInput(
            hint_text="Minutes (1 - 60)", multiline=False, halign="center", font_size=20,
            background_color=(0, 0, 0, 0), foreground_color=(0, 0, 0, 1)
        )
        input_box.add_widget(self.timer_input)
        self.add_widget(input_box)

        timer_btn = Button(text="Set Timer", size_hint=(1, 0.5),
                           background_color=(0.1, 0.5, 0.8, 1), font_size=18)
        timer_btn.bind(on_press=self.set_timer)
        self.add_widget(timer_btn)

        self.countdown_label = Label(text="Time: --:--", font_size=28,
                                     color=(0.2, 0.2, 0.2, 1), bold=True, size_hint=(1, 0.6))
        self.add_widget(self.countdown_label)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def set_timer(self, instance):
        if self.onoff_control.status_label.text != "AC is ON":
            self.countdown_label.text = "AC is OFF - Can't set timer!"
            return

        minutes = self.timer_input.text
        if minutes.isdigit():
            minutes = int(minutes)
            if 1 <= minutes <= 60:
                self.remaining_seconds = minutes * 60
                self.update_countdown(0)
                if self.timer_event:
                    self.timer_event.cancel()
                self.timer_event = Clock.schedule_interval(self.update_countdown, 1)
                time_str = f"{minutes:02d}:00"
                self.api.update_timer(time_str)
            else:
                self.countdown_label.text = "Enter 1 to 60 minutes only!"
        else:
            self.countdown_label.text = "Invalid time!"

    def update_countdown(self, dt):
        if self.remaining_seconds > 0:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.countdown_label.text = f"Time: {time_str}"
            self.api.update_timer(time_str)
            self.remaining_seconds -= 1
        else:
            self.countdown_label.text = "AC turned OFF"
            self.onoff_control.turn_off()
            if self.timer_event:
                self.timer_event.cancel()


# --- Main App ---
class ACRemoteApp(App):
    def build(self):
        Window.size = (300, 550)
        Window.clearcolor = (1, 1, 1, 1)

        self.api = MockAPIService()
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        self.onoff_control = OnOffControl(self.api)
        layout.add_widget(self.onoff_control)

        self.temp_control = TemperatureControl(self.api)
        layout.add_widget(self.temp_control)

        self.timer_control = TimerControl(self.api, self.onoff_control)
        layout.add_widget(self.timer_control)

        return layout


if __name__ == "__main__":
    ACRemoteApp().run()
