import esprima

PATH="/home/jdnietov/Development/meetin/imports/ui/pages/activityPurchase.js"
code = open(PATH, "r")
tree = esprima.parseModule(code.read())
code.close()
print(tree)
