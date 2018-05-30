import esprima
import os
import kivy
kivy.require('1.0.6')
from kivy.app import App
from kivy.uix.label import Label

PROJECT_PATH="/home/jdnietov/Development/meteorapp"
PROJECT_FILES=[]

class MyApp(App):
    def build(self):
        return Label(text='Hello world')


def sliceLast(path):
    idx = len(path)-1
    while path[idx] != '/':
        idx = idx - 1
    return [path[idx+1:], path[:idx]]

def isExternalModule(path):
    return not path[0] == '.' and not path[0] == '/'

class MeteorVar:
    name = ""
    type = ""

class BlazeFunction:
    name = ""
    args = ""

    def __init__(self, name, args):
        self.name = name
        self.args = args

    def printInfo(self):
        argsStr = ["("]
        for arg in self.args:
            argsStr.append(arg)
            argsStr.append(",")
        argsStr[len(argsStr)-1] = ")"
        print self.name + "".join(argsStr)

class BlazeEvent(BlazeFunction):
    event = ""

class BlazeTemplate:
    def __init__(self, name):
        self.name = name
        self.localVariables = []
        self.methods = {
            "helpers": [],
            "events": []
        }

    def initOnCreated(self, meteorVars):
        self.onCreated = meteorVars   # TODO:

    def addFunctionToMethod(self, methodName, function):
        methods = self.methods
        if methodName in methods:
            methods[methodName].append(function)
            return True
        else:
            print "*** BlazeError: no Blaze method is named " + methodName
            return False


class ProjectFile:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.templates = {}
        self.variables = []
        self.funcs = []
        self.imports = []
    
    def getSyntaxTree(self):
        file = open(self.path + "/" + self.name, "r")
        tree = esprima.parseModule(file.read())
        file.close()
        # print(tree)
        return tree

    def addImport(self, dependency):
        self.imports.append(dependency)

    def hasTemplate(self, name): 
        return name in self.templates

    def addTemplate(self, templateName):
        self.templates[templateName] = BlazeTemplate(templateName)

    def getTemplate(self, templateName):
        return self.templates[templateName]

    def addFunctionToMethod(self, templateName, methodName, blazeFunction):
        if templateName in self.templates:
            return self.templates[templateName].addFunctionToMethod(methodName, blazeFunction)
        else:
            # print("ERROR:", templateName, "is not defined inside", self.name)
            return False

    def printInfo(self):
        print "File:", self.name
        print self.path + "/" + self.name
        print "*****\nTemplates included:"
        for name in self.templates:
            template = self.templates[name]
            print "\t" + template.name
            print template.methods
        
class Module(object):
    def __init__(self, path):
        self.default = ""
        self.consts = []
        self.relativePath = path
        self.file = None
    
    def addConst(self, const):
        self.consts.append(const)

    def printDep(self):
        # print(self.relativePath, self.default, self.consts)
        return 0
    
class ProjectModule(Module):
    def __init__(self, name, path):
        super(ProjectModule, self).__init__(path + "/" + name)
        self.file = ProjectFile(name, path)



def fabricateModule(fullpath):
    name, path = sliceLast(fullpath)
    if name[0] == '.' or name[0] == '/':
        return ProjectModule(name, path)
    else:
        return Module(fullpath)


def parse(file):
    tree = file.getSyntaxTree()

    for statement in tree.body:
        if statement.type == 'ImportDeclaration':
            specifiers = statement.specifiers
            module = fabricateModule(statement.source.value.encode('ascii'))

            for spec in specifiers:
                importName = spec.local.name.encode('ascii')
                if spec.type == 'ImportSpecifier':
                    module.addConst(importName)
                elif spec.type == 'ImportDefaultSpecifier':
                    module.default = importName

            module.printDep()
            file.addImport(module)

        elif statement.type == 'ExpressionStatement':
            expression = statement.expression
            callee = expression.callee

            if callee.type == 'MemberExpression' and callee.object.object.name == "Template":
                templateName = callee.object.property.name.encode('ascii')

                if not file.hasTemplate(templateName):
                    file.addTemplate(templateName)

                methodName = callee.property.name
                if methodName == "onCreated":
                    pass

                if methodName == "helpers":
                    functions = expression.arguments[0].properties
                    for f in functions:
                        functionName = f.key.name.encode('ascii')
                        params = f.value.params
                        args = []
                        for param in params:
                            args.append(param.name.encode('ascii'))
                        function = BlazeFunction(functionName, args)
                        file.addFunctionToMethod(templateName, methodName, function)

                elif methodName == "events":
                    functions = expression.arguments[0].properties
                    for f in functions:
                        functionName = f.key.value
                        args = []
                        for param in params:
                            args.append(param.name.encode('ascii'))
                        function = BlazeFunction(functionName, args)
                        file.addFunctionToMethod(templateName, methodName, function)
                
    file.printInfo()
                    

def main():
    # PROJECT_PATH=raw_input()
    MyApp().run()
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)            
            PROJECT_FILES.append(f)            
            break

    for file in PROJECT_FILES:
        parse(file)

main()