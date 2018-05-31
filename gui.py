import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.gridlayout import GridLayout

class Container(GridLayout):
    pass

class Spacecraft(App):
    def build(self):
        self.title = 'Spacecraft! - software visualizer for Meteor.js projects'
        return Container()
