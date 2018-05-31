def slicelast(path):
    idx = len(path)-1
    while path[idx] != '/':
        idx = idx - 1
    return [path[idx+1:], path[:idx]]

def isextmodule(path):
    return not path[0] == '.' and not path[0] == '/'