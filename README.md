# Spacecraft - Meteor.js Visualizer

by José David Nieto, for Lenguajes de Programación 2018-I. Universidad Nacional de Colombia.

## Dependencies
- [esprima-python by Kronuz](https://github.com/Kronuz/esprima-python) to perform lexical and syntactic analysis on Javascript files
- [Treelib by caesar0301](https://github.com/caesar0301/treelib) to print recursive data structures.

`pip install --user esprima treelib`

## Usage
`python3 main.py [-h] [-v] proj_path [file_path]`
- `-h`: help
- `-v`: verbose - print (a lot) about file loading
- `proj_path`: path to Meteor.js project
- `file_path`: relative path inside `proj_path` towards a particular file

## Test
`python3 main.py test/meteorapp`