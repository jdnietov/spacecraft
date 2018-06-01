import os
import esprima
import networkx as nx
from treelib import Node, Tree
from dirstrs import isnpm, importpath, slicefile, ext

PROJECT_PATH="/home/jdnietov/Development/meetin/"
NFILES=0

OPT_VERBOSE=False


#
# ─── CLASS DEFINITIONS ──────────────────────────────────────────────────────────
#

class File(object):
    def __init__(self, name, path):
        global NFILES
        self.id = NFILES
        self.fname = name
        self.path = os.path.relpath(path, PROJECT_PATH)
        NFILES = NFILES + 1
        # print("~ new file added:", self.fullpath())
    
    def __hash__(self):
        return hash(self.fullpath())
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.fname == other.fname and self.path == other.path

    def fullpath(self):
        return self.path + "/" + self.fname
    
    def tag(self):
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
        print(self.name + "".join(argsStr))

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
            print("*** BlazeError: no Blaze method is named " + methodName)
            return False

class ProjectFile(File):
    def __init__(self, name, path):
        super(ProjectFile, self).__init__(name, path)     
        self.templates = {}
        self.variables = []
        self.funcs = []
        self.imports = []
    
    def importTree(self):
        tree = Tree()
        tree.create_node(self.fname, self.fname)
        # TODO:

    def load(self):
        new_files = []
        tree = self.getSyntaxTree()

        for statement in tree.body:
            if statement.type == 'ImportDeclaration':
                specifiers = statement.specifiers
                module = createmodule(self.path, self.fname, statement.source.value)

                for spec in specifiers:
                    importName = spec.local.name
                    if spec.type == 'ImportSpecifier':
                        module.addConst(importName)
                    elif spec.type == 'ImportDefaultSpecifier':
                        module.default = importName

                if module.hasFile:
                    new_files.append(module.file)

                self.addImport(module)

            elif statement.type == 'ExpressionStatement':
                expression = statement.expression
                callee = expression.callee

                if expression.type == "CallExpression" and callee.type == 'MemberExpression':
                    if callee.object.object is None:
                        pass
                    elif callee.object.object.name == "Template":
                        templateName = callee.object.property.name

                        if not self.hasTemplate(templateName):
                            self.addTemplate(templateName)

                        methodName = callee.property.name
                        if methodName == "onCreated":
                            pass

                        if methodName == "helpers":
                            functions = expression.arguments[0].properties
                            for f in functions:
                                functionName = f.key.name
                                params = f.value.params
                                args = []
                                for param in params:
                                    args.append(param.name)
                                function = BlazeFunction(functionName, args)
                                self.addFunctionToMethod(templateName, methodName, function)

                        elif methodName == "events":
                            functions = expression.arguments[0].properties
                            for f in functions:
                                functionName = f.key.value
                                params = f.value.params
                                args = []
                                for param in params:
                                    args.append(param.name)
                                function = BlazeFunction(functionName, args)
                                self.addFunctionToMethod(templateName, methodName, function)
                    
                    else:
                        print("!! TODO: process files without templates")

        return new_files

    def getSyntaxTree(self):
        # fp = os.path.join(PROJECT_PATH, self.path) + "/" + self.fname
        fp = PROJECT_PATH + self.path + "/" + self.fname
        print("~ loading file from", fp)
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
        print("**********")
        print(self.fullpath())
        for name in self.templates:
            template = self.templates[name]
            print("- [template] " + template.tname)
            # print template.methods
            for method in template.methods:
                print(" * " + method)
                for function in template.methods[method]:
                    function.printFunc()
    
    def tag(self):
        if len(self.templates) > 0:
            return self.path + "/" + self.fname + " [Template]" 
        else:
            return self.path + "/" + self.fname 
        
class Module(object):
    def __init__(self, frompath, fromfile, path):
        self.default = ""
        self.consts = []
        self.fromfile = fromfile
        self.frompath = frompath
        self.path = path
        self.hasFile = False
    
    def addConst(self, const):
        self.consts.append(const)
    
class ProjectModule(Module):
    def __init__(self, frompath, fromfile, path):
        super(ProjectModule, self).__init__(frompath, fromfile, path)
        self.isExternal = True

class JSModule(ProjectModule):
    def __init__(self, frompath, fromfile, fullpath):
        super(JSModule, self).__init__(frompath, fromfile, fullpath)
        path, name = slicefile(fullpath)
        self.file = ProjectFile(name, importpath(PROJECT_PATH, frompath, path))
        self.hasFile = True

def createmodule(frompath, fromfile, path):
    # print("// frompath:", frompath, ", path:", path)
    if not isnpm(path):
        if ext(path) == "js":
            print("[!] JS module imported:", path)
            return JSModule(frompath, fromfile, path)
        else:
            print("[*] markup module imported:", path)
            return ProjectModule(frompath, fromfile, path)
    else:
        print("[-] npm module imported:", path)
        return Module(frompath, fromfile, path)



#
# ─── PROJECT VISUALIZATION METHODS ──────────────────────────────────────────────
#

def generateTree(rootFile):
    files = rootFile.load()

    rootId = rootFile.id
    rootTag = rootFile.tag()
    myTree = Tree()
    myTree.create_node(rootTag, rootId)    

    for file in files:
        myTree.paste(rootId, generateTree(file))
    
    return myTree


#
# ─── MAIN MODULE ────────────────────────────────────────────────────────────────
#
    
def main():
    # PROJECT_PATH=raw_input()
    main = {}
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            main = ProjectFile("main.js", dirpath)
            break

    tree = generateTree(main)
    tree.show()
    # generateGraph(main)

main()