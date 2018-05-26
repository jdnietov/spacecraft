import esprima
import os

PROJECT_PATH="/home/jdnietov/Development/meteorapp"
PROJECT_FILES=[]

class BlazeFunction:
    name = ""
    args = ""

    def __init__(self, name, args):
        self.name = name
        self.args = args

class BlazeEvent(BlazeFunction):
    event = ""

class BlazeTemplate:
    name = ""
    onCreated = {}
    methods = {
        "helpers": [],
        "events": []
    }

    def __init__(self, name):
        self.name = name

    def initOnCreated(self, body):
        self.onCreated = body   # TODO:

    def addFunctionToMethod(self, methodName, function):
        if methodName in methods:
            methods[methodName].append(function)
        else:
            print("ERROR: no Blaze method is named", methodName)


class ProjectFile:
    name = ""
    path = ""

    templates = []
    variables = []
    funcs = []
    dependencies = []

    def __init__(self, name, path):
        self.name = name
        self.path = path
    
    def getSyntaxTree(self):
        file = open(self.path + "/" + self.name, "r")
        tree = esprima.parseModule(file.read())
        file.close()
        return tree

    def hasTemplate(self, name): 
        for template in self.templates:
            if template.name == name:
                return True
        return False

    def addTemplate(self, templateName):
        self.templates.append(BlazeTemplate(templateName))

    def addFunctionToMethod(self, templateName, methodName, blazeFunction):
        tidx = False
        for t in range(len(self.templates)):
            if self.templates[t].name == templateName:
                tidx = t

        if not template:
            print("ERROR:", templateName, "is not defined inside", self.name)
            return False
        
        return self.templates[tidx].addFunctionToMethod(methodName, blazeFunction)

        


def parse(file):
    tree = file.getSyntaxTree()
    methods = []

    for statement in tree.body:
        if statement.type == 'ImportDeclaration':
            print("TODO: dependencies")
        if statement.type == 'ExpressionStatement':
            callee = statement.expression.callee
            if callee.type == 'MemberExpression' and callee.object.object.name == "Template":
                name = callee.object.property.name

                if not file.hasTemplate(name):
                    file.addTemplate(name)

                method = callee.property.name
                print(method)                

def main():
    # PROJECT_PATH=raw_input()

    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)            
            PROJECT_FILES.append(f)            
            break

    for file in PROJECT_FILES:
        parse(file)

main()