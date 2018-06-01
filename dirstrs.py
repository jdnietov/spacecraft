def slicefile(path):
    idx = len(path)-1
    while idx >= 0 and path[idx] != '/':
        idx = idx - 1
    return [path[:idx], path[idx+1:]]

def isnpm(path):
    return not path[0] == '.' and not path[0] == '/'

def ext(path):
    idx = path.rfind('.')
    if idx > 0:
        return path[path.rfind('.')+1:]
    else:
        return ""

def importpath(rootpath, relpath, path):
    if path[0] == '.':
        if not relpath.endswith('/'):
            relpath += '/'
        return rootpath + relpath + path
    elif path[0] == '/':
        return rootpath + path[1:]