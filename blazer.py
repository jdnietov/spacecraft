import esprima
from dirstrs import slicelast, isnpm, ext

class File(object):
    def __init__(self, name, path):
        self.fname = name
        self.path = path
        print self.fullpath()

    def fullpath(self):
        return self.path + "/" + self.fname        

class BlazeFunction:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def printFunc(self):
        argsStr = ["("]
        for arg in self.args:
            argsStr.append(arg)
            argsStr.append(",")
        argsStr[len(argsStr)-1] = ")"
        print self.name + "".join(argsStr)

class BlazeTemplate:
    def __init__(self, name):
        self.tname = name
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

class ProjectFile(File):
    def __init__(self, name, path):
        super(ProjectFile, self).__init__(name, path)     
        self.templates = {}
        self.variables = []
        self.funcs = []
        self.imports = []

        self.__load()
    
    def __load(self):
        tree = self.getSyntaxTree()

        for statement in tree.body:
            if statement.type == 'ImportDeclaration':
                specifiers = statement.specifiers
                module = createmodule(statement.source.value.encode('ascii'))

                for spec in specifiers:
                    importName = spec.local.name.encode('ascii')
                    if spec.type == 'ImportSpecifier':
                        module.addConst(importName)
                    elif spec.type == 'ImportDefaultSpecifier':
                        module.default = importName

                module.printDep()
                self.addImport(module)

            elif statement.type == 'ExpressionStatement':
                expression = statement.expression
                callee = expression.callee

                if callee.type == 'MemberExpression' and callee.object.object.name == "Template":
                    templateName = callee.object.property.name.encode('ascii')

                    if not self.hasTemplate(templateName):
                        self.addTemplate(templateName)

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
                            self.addFunctionToMethod(templateName, methodName, function)

                    elif methodName == "events":
                        functions = expression.arguments[0].properties
                        for f in functions:
                            functionName = f.key.value
                            args = []
                            for param in params:
                                args.append(param.name.encode('ascii'))
                            function = BlazeFunction(functionName, args)
                            self.addFunctionToMethod(templateName, methodName, function)

    def getSyntaxTree(self):
        fp = self.fullpath()
        code = open(fp, "r")
        tree = esprima.parseModule(code.read())
        code.close()
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
        print "File:", self.fname
        print self.fullpath()
        print "*****\nTemplates included:"
        for name in self.templates:
            template = self.templates[name]
            print "\t" + template.tname
            # print template.methods
            for method in template.methods:
                print "\t\t" + method
                for function in template.methods[method]:
                    function.printFunc()
        
class Module(object):
    def __init__(self, path):
        self.default = ""
        self.consts = []
        print path
        self.relativePath = path
    
    def addConst(self, const):
        self.consts.append(const)

    def printDep(self):
        # print(self.relativePath, self.default, self.consts)
        return 0
    
class ProjectModule(Module):
    def __init__(self, name, path):
        super(ProjectModule, self).__init__(path + "/" + name)
        self.isExternal = True

class JSModule(ProjectModule):
    def __init__(self, name, path):
        super(JSModule, self).__init__(name, path)
        self.file = ProjectFile(name, path)

def createmodule(fullpath):
    path, name = slicelast(fullpath)
    if not isnpm(path):
        if ext(name) == "js":
            return JSModule(name, path)
        else:
            return ProjectModule(name, path)
    else:
        return Module(fullpath)