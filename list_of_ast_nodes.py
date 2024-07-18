import ast

# Function to get all classes in the ast module that represent AST nodes
def get_ast_node_types():
    node_types = []
    for name in dir(ast):
        # Get the attribute
        attr = getattr(ast, name)
        # Check if it's a class and a subclass of ast.AST
        if isinstance(attr, type) and issubclass(attr, ast.AST):
            node_types.append(name)
    return node_types

# Get and print all AST node types
ast_node_types = get_ast_node_types()
print(ast_node_types)