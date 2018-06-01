import os
import sys
import esprima
import argparse
import networkx as nx
from treelib import Node, Tree
from dirstrs import isnpm, importpath, slicefile, ext

PROJECT_PATH="/home/jdnietov/Development/meetin/"
FILE_PATH=""
OPT_VERBOSE=False
NFILES=0


#
# ─── CLASS DEFINITIONS ──────────────────────────────────────────────────────────
#

class File(object):
    def __init__(self, name, path):
        global NFILES
        self.id = NFILES
        self.fname = name
        self.path = os.path.relpath(path, PROJECT_PATH)
        # print("~ new file added:", self.fullpath())
        NFILES = NFILES + 1
    
    def __hash__(self):
        return hash(self.fullpath())
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.fname == other.fname and self.path == other.path

    def fullpath(self):
        return self.path + "/" + self.fname
    
    def tag(self):
        return self.path + "/" + self.fname
        

class BlazeFunction(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def tostr(self):
        argsStr = [""]
        for arg in self.args:
            argsStr.append(arg)
            argsStr.append(",")
        argsStr[len(argsStr)-1] = ")"
        return self.name + "(" + "".join(argsStr)

class BlazeEvent(BlazeFunction):
    def __init__(self, name, args):
        super(BlazeEvent, self).__init__(name, args)
        event, target = name.split()
        self.event = event
        self.target = target
    
    def tostr(self):
        argsStr = [""]
        for arg in self.args:
            argsStr.append(arg)
            argsStr.append(",")
        argsStr[len(argsStr)-1] = ")"
        return self.event + " > '" + self.target + "' (" + "".join(argsStr)


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

class ProjectFile(File):
    def __init__(self, name, path):
        super(ProjectFile, self).__init__(name, path)     
        self.templates = {}
        self.variables = []
        self.funcs = []
        self.imports = []
        self.parsed = False

    def parse(self, tree):
        if self.parsed:
            return

        for statement in tree.body:
            if statement.type == 'ExpressionStatement':
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
                                function = BlazeEvent(functionName, args)
                                self.addFunctionToMethod(templateName, methodName, function)
                    
                    else:
                        print("!! TODO: process files without templates")
        
        self.parsed = True

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

        self.parse(tree)

        return new_files

    def getSyntaxTree(self):
        global OPT_VERBOSE
        fp = PROJECT_PATH + self.path + "/" + self.fname

        if OPT_VERBOSE:
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
        self.parse(self.getSyntaxTree())

        divider=""
        title=self.fname + " | at " + self.fullpath()
        for c in title:
            divider += "─"
        print(title)
        print(divider)

        if len(self.templates) == 0:
            print("This file does not include a Blaze template.\n")
        else:
            for name in self.templates:
                template = self.templates[name]
                print("{{> " + template.tname + " }} template")

                for method in template.methods:
                    tree = Tree()
                    tree.create_node("[ " + method + " ]", method)
                    for function in template.methods[method]:
                        funcstr = function.tostr()
                        tree.create_node(funcstr, funcstr, parent=method)
                    tree.show()
    
    def tag(self):
        if len(self.templates) > 0:
            return self.path + "/" + self.fname + " [Template]" 
        else:
            return self.path + "/" + self.fname 
        

def createmodule(frompath, fromfile, path):
    if not isnpm(path):
        if ext(path) == "js":
            if OPT_VERBOSE:
                print("[!] JS module imported:", path)
            return JSModule(frompath, fromfile, path)
        else:
            if OPT_VERBOSE:            
                print("[*] markup module imported:", path)
            return ProjectModule(frompath, fromfile, path)
    else:
        if OPT_VERBOSE:
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

def printError(message):
    print("\n! ! !     E r r o r     ! ! !")
    print("⁕ Your Spacecraft run crashed, and so did you!")
    print("⁕ " + message + "\n")
    print("– See you, space cowboy!")
        

#
# ─── MAIN MODULE ────────────────────────────────────────────────────────────────
#
    
def main():
    global OPT_VERBOSE, PROJECT_PATH, FILE_PATH
    parser = argparse.ArgumentParser(description='Generate visualizations of project dependencies in Meteor.js.')
    parser.add_argument('PROJECT_PATH', metavar='proj_path', type=str,
                   help='Path to the Meteor.js project.')
    parser.add_argument('FILE_PATH', metavar='file_path', type=str, default="", nargs="?",
                   help='Path to the Meteor.js file you want the dependency tree of.')
    parser.add_argument('-v', dest='OPT_VERBOSE', action='store_true', help='print stuff')
    args = parser.parse_args()

    OPT_VERBOSE=args.OPT_VERBOSE
    PROJECT_PATH=args.PROJECT_PATH
    FILE_PATH=args.FILE_PATH

    if not PROJECT_PATH.endswith('/'):
        PROJECT_PATH += '/'
    if FILE_PATH.endswith('/'):
        FILE_PATH += FILE_PATH[1:]

    print("Spacecraft - console explorer for Meteor.js projects")
    print("––––––––––––––––––––––––––––––––––––––––––––––––––––\n")
    main = {}

    print("• • • Verifying source... • • •")
    
    dirfiles = os.listdir(PROJECT_PATH)

    if "package.json" in dirfiles and ".meteor" in dirfiles:
        print("– Meteor.js project found in " + PROJECT_PATH + "\n")
        for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
            if "main.js" in filenames:
                main = ProjectFile("main.js", dirpath)
                break
    else:
        printError(PROJECT_PATH + " is not a Meteor.js project.")
        return

    if len(FILE_PATH) > 0:
        print("• • • Aditional files... • • •")
        if os.path.isfile(PROJECT_PATH + FILE_PATH):
            print(PROJECT_PATH + FILE_PATH + " was found. \n")
            path, name = slicefile(FILE_PATH)
            main = ProjectFile(name, PROJECT_PATH + path)
        else:
            printError(FILE_PATH + " was not found.")

    
    # print("\n• • • We're ready for ignition! • • •\n\n")


    main.printInfo()
    print("───────── Dependency tree for " + main.fname + " ─────────")
    tree = generateTree(main)
    tree.show()

main()