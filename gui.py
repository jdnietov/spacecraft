import kivy
kivy.require('1.0.6')
from kivy.app import App
from kivy.uix.label import Label

class Spacecraft(App):
    def build(self):
        return Label(text='Hello world')