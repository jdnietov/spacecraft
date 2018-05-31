def slicelast(path):
    idx = len(path)-1
    while path[idx] != '/':
        idx = idx - 1
    return [path[:idx], path[idx+1:]]

def isnpm(path):
    return not path[0] == '.' and not path[0] == '/'

def ext(path):
    idx = path.rfind('.')
    print "path: " + path
    print "extension of file: " + path[path.rfind('.')+1:]
    if idx > 0:
        return path[path.rfind('.')+1:]
    else:
        return ""