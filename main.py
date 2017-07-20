import json
import random

from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.factory import Factory


class AddLocationForm(BoxLayout):  # the root class in the KV language file
    search_input = ObjectProperty()
    search_results = ObjectProperty()

    def search_location(self):
        if len(self.search_input.text) != 0:
            content = Button(text='Dismiss', height=dp(40), size_hint_y=None)
            popup = Popup(title="Please wait while we search for '{}'".format(self.search_input.text), content=content,
                          size_hint=(None, None), size=(400, 150), auto_dismiss=False)
            content.bind(on_press=popup.dismiss)

            search_template = "http://api.openweathermap.org/data/2.5/" + "find?q={}&type=like&APPID=5cc1da8c59b625759c95307e0b38b3fc"
            search_url = search_template.format(self.search_input.text)
            print(search_url)
            print("finding location.........")
            request = UrlRequest(search_url, self.found_location)
            popup.open()
            print("The user searched for '{}'".format(self.search_input.text))
        else:
            popup = Popup(title='Error', content=Label(text="Please enter a known city."), size_hint=(None, None), size=(400, 100),
                          auto_dismiss=True)
            popup.open()

    def found_location(self, request, data):
        try:
            data = json.loads(data.decode()) if not isinstance(data, dict) else data
            cities = [(d['name'], d['sys']['country']) for d in data['list']]
            self.search_results.item_strings = cities
            self.search_results.adapter.data = []
            self.search_results.adapter.data.extend(cities)
            self.search_results._trigger_reset_populate()
            print("function found_location searched")
            print(data)
        except UnicodeEncodeError as e:
            self.label_set_error.text = "City '{}' not found".format(self.search_input.text)
            print("City not found.".format(e))

    def current_location(self):
        search_url = "http://api.openweathermap.org/data/2.5/" + "find?lat=3.8667&lon=11.5167&APPID=5cc1da8c59b625759c95307e0b38b3fc"
        print(search_url)
        print('finding location.........')
        request = UrlRequest(search_url, self.found_location)

    def on_enter(self):
        self.search_location()

    @staticmethod
    def args_converter(index, data_item):
        city, country = data_item
        return {'location': (city, country)}


class CurrentWeather(BoxLayout):
    current_conditions = ObjectProperty()

    location = ListProperty(['Yaounde', 'CM'])
    conditions = ObjectProperty()
    temp = NumericProperty()
    temp_min = NumericProperty()
    temp_max = NumericProperty()

    def update_weather(self):
        try:
            weather_template = "http://api.openweathermap.org/data/2.5/" + "weather?q={},{}&units=metric&APPID=5cc1da8c59b625759c95307e0b38b3fc"
            weather_url = weather_template.format(*self.location)
            request = UrlRequest(weather_url, self.weather_retrieved)
        except request.error as e:
            print('Connection lost.'.format(e))

    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.render_conditions(data['weather'][0]['description'])
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']

    def render_conditions(self, conditions_description):
        if "clear" in conditions_description.lower():
            conditions_widget = Factory.ClearConditions()
        elif "snow" in conditions_description.lower():
            conditions_widget = SnowConditions()
        else:
            conditions_widget = Factory.UnknownConditions()
        conditions_widget.conditions = conditions_description
        self.conditions.clear_widgets()
        self.conditions.add_widget(conditions_widget)


class WeatherRoot(BoxLayout):
    current_weather = ObjectProperty()

    def show_current_weather(self, location=None):
        self.clear_widgets()

        if self.current_weather is None:
            self.current_weather = CurrentWeather()
        if location is not None:
            self.current_weather.location = location
        self.current_weather.update_weather()
        self.add_widget(self.current_weather)

    def show_add_location_form(self):
        self.clear_widgets()
        location_form = AddLocationForm()
        self.add_widget(location_form)


class Conditions(BoxLayout):
    conditions = StringProperty()


class SnowConditions(Conditions):
    FLAKE_SIZE = 5
    NUM_FLAKES = 60
    FLAKE_AREA = FLAKE_SIZE * NUM_FLAKES
    FLAKE_INTERVAL = 1.0 / 30.0

    def __init__(self, **kwargs):
        super(SnowConditions, self).__init__(**kwargs)
        self.flakes = [[x * self.FLAKE_SIZE, 0] for x in range(self.NUM_FLAKES)]
        Clock.schedule_interval(self.update_flakes, self.FLAKE_INTERVAL)

    def update_flakes(self, time):
        for f in self.flakes:
            f[0] += random.choice([-1, 1])
            f[1] -= random.randint(0, self.FLAKE_SIZE)
            if f[1] <= 0:
                f[1] = random.randint(0, int(self.height))

        self.canvas.before.clear()
        with self.canvas.before:
            widget_x = self.center_x - self.FLAKE_AREA / 2
            widget_y = self.pos[1]
            for x_flake, y_flake in self.flakes:
                x = widget_x + x_flake
                y = widget_y + y_flake
                Color(0.9, 0.9, 1.0)
                Ellipse(pos=(x, y), size=(self.FLAKE_SIZE, self.FLAKE_SIZE))


class LocationButton(ListItemButton):
    location = ListProperty()


class WeatherApp(App):
    pass


if __name__ == '__main__':
    WeatherApp().run()
