import esprima
from dirstrs import slicelast

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

def createmodule(fullpath):
    name, path = slicelast(fullpath)
    if name[0] == '.' or name[0] == '/':
        return ProjectModule(name, path)
    else:
        return Module(fullpath)