from sys import argv
import tokenize
import os
import ast
import json

class FileReader:
    """
        Basic File handler.
    """

    def __init__(self, path: str = ''):
        self.path = path
        self.files = None

    def return_entire_file(self):
        with open(self.path, 'r') as file:
            file = file.read()
        return file
    
    def return_line_list(self):
        with open(self.path, 'rd') as file:
            file = [line for line in file]
        return file
    
    def return_readline_ref(self):
        with open(self.path, 'rd') as file:
            file = file.readline
        return file
    
    def return_all_files(self, excluded: list, ext: str = '') -> list:
        file_list = []
        if ext:
            for root, dirs, files in os.walk(self.path):
                dirs[:] = [d for d in dirs if d not in excluded]
                for file in files:
                    if file.endswith(ext):
                        file_list.append(os.path.join(root, file))
        else:
            for root, dirs, files in os.walk(self.path):
                dirs[:] = [d for d in dirs if d not in excluded]
                for file in files:
                    file_list.append(os.path.join(root, file))
        return file_list

class ParseCode(FileReader):
    
    def __init__(self, path: str = ''):
        super().__init__(path=path)
        self.name = path.replace('.py', '').split('/')[-1]

    def return_ast(self):
        return ast.parse(self.return_entire_file(), type_comments=True)
    
    def return_all_files(self, excluded: list, ext: str = None) -> list:
        return [ParseCode(path=path) for path in super().return_all_files(excluded, ext)]
    
    def return_ast_dump(self):
        return ast.dump(ast.parse(self.return_entire_file()), indent=4)

    def return_token_list(self):
        tokens = tokenize.tokenize(self.return_readline_ref())
        return [token for token in tokens]

class Converter:

    def ast_to_dict(self, node: str = ''):
        if isinstance(node, ast.AST):
            node_dict = {k: self.ast_to_dict(getattr(node, k)) for k in node._fields}
            node_dict['_type'] = node.__class__.__name__
            return node_dict
        elif isinstance(node, list):
            return [self.ast_to_dict(elem) for elem in node]
        return node

    def convert_ast_to_json(self, ast: ast.AST):
        return json.dumps(self.ast_to_dict(ast), indent=2)
    
    def return_dict(self, ast: ast.AST):
        return self.ast_to_dict(ast)