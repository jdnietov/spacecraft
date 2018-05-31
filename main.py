import os

from dirstrs import isnpm
from gui import Spacecraft
from blazer import ProjectFile, BlazeFunction, createmodule

PROJECT_PATH="/home/jdnietov/Development/meteorapp"
PROJECT_FILES=[]

def main():
    # PROJECT_PATH=raw_input()
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)         
            f.printInfo()        
            PROJECT_FILES.append(f)            
            break
    
    Spacecraft().run()
    

main()