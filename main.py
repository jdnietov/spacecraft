import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.lang import Builder

import os

from dirstrs import isnpm
from templateWidget import TemplateWidget
from blazer import ProjectFile, BlazeFunction, createmodule

Builder.load_file('customfilechooserview.kv')
Builder.load_file('scgrid.kv')
Builder.load_file('templatewidget.kv')

PROJECT_PATH="/home/jdnietov/Development/meteorapp"
PROJECT_FILES=[]

class CustomFileChooserView(FileChooserListView):
    pass

class TemplateWidget(Widget):
    pass

class ScGrid(GridLayout):
    pass

class SpacecraftApp(App):        
    def build(self):
        self.title = 'Spacecraft! - software visualizer for Meteor.js projects'
        return ScGrid()

def main():
    # PROJECT_PATH=raw_input()
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)         
            f.printInfo()        
            PROJECT_FILES.append(f)            
            break
    
    spacecraft = SpacecraftApp()
    spacecraft.run()    

main()