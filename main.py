import esprima
import os 
import glob

class ProjectFile:
    name=""
    path=""

    variables = []
    funcs=[]
    dependencies=[]

    def __init__(self, name, path):
        self.name = name
        self.path = path
    
    def getCode(self):
        file = open(self.path + "/" + self.name, "r")
        code = file.read()
        file.close()
        return code

class ProjectTemplate(ProjectFile):
    methods = {
        "helpers": {},
        "events": {}
    }

    def addMethod(name, value):


PROJECT_PATH=""
PROJECT_FILES=[]

def parse(file):
    tokens = esprima.tokenize(file.getCode())

    templateName = ""
    print(tokens)
    
    i = 0
    while i < len(tokens):
        # TODO: include Template dependency
        if tokens[i].type == "Identifier" and tokens[i].value == "Template":
            if len(templateName) > 0:
                templateName = tokens[i+2].value
            
            i = i + 4
            method = ""
            if tokens[i].type == "Identifier":
                method = tokens[i].value
                print(method)

        i = i + 1

def main():
    PROJECT_PATH=raw_input()

    # get main.js code - wherever it is
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)

            print(f.getCode())
            
            PROJECT_FILES.append(f)            
            break

    for file in PROJECT_FILES:
        parse(file)

main()