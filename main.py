import json

from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListItemButton
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty

from kivy.factory import Factory


class AddLocationForm(BoxLayout):  # the root class in the KV language file
    search_input = ObjectProperty()
    search_results = ObjectProperty()
    label_set_error = ObjectProperty()

    def search_location(self):
        try:
            search_template = "http://api.openweathermap.org/data/2.5/" + "find?q={}&type=like&APPID=5cc1da8c59b625759c95307e0b38b3fc"
            search_url = search_template.format(self.search_input.text)
            print(search_url)
            print("finding location.........")
            request = UrlRequest(search_url, self.found_location)
            print("The user searched for '{}'".format(self.search_input.text))
        except request.error as e:
            print("Connection Lost.".format(e))

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
    location = ListProperty(['Yaounde', 'CM'])
    conditions = StringProperty()
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
        self.conditions = data['weather'][0]['description']
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']


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


class LocationButton(ListItemButton):
    location = ListProperty()


class WeatherApp(App):
    pass


if __name__ == '__main__':
    WeatherApp().run()
