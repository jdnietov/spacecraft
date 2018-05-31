import os

from dirstrs import isextmodule
from gui import Spacecraft
from blazer import ProjectFile, BlazeFunction, createmodule

PROJECT_PATH="/home/jdnietov/Development/meteorapp"
PROJECT_FILES=[]

def parse(file):
    tree = file.getSyntaxTree()

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
    for (dirpath, dirnames, filenames) in os.walk(PROJECT_PATH):
        if "main.js" in filenames:
            f = ProjectFile("main.js", dirpath)            
            PROJECT_FILES.append(f)            
            break

    for file in PROJECT_FILES:
        parse(file)
    
    Spacecraft().run()
    

main()