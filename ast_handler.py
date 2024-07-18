from typing import Any, Union, IO
import reader
from pathlib import Path
from gpt4all import GPT4All

PYTHON_EXCLUDED = [
    'venv', 
    '.git', 
    '.idea' 
    '__pycache__', 
]

HANDLED_EXPRESISONS = [
    'try',
    'if',
    'classdef',
    'functiondef',
    'assign',
    'import',
    'importfrom',
    'annassign',
    'delete',
    'expr',
    'for',
    'while',
    'global', 
    'return', 
    'continue',
    'augassign',
    'with',
    'raise',
    'break',
    'pass',
    'assert'
    ]

possible_nodes = [
    'AST', 'Add', 'And', 'AnnAssign', 'Assert', 'Assign', 'AsyncFor', 'AsyncFunctionDef', 'AsyncWith', 'Attribute', 
    'AugAssign', 'AugLoad', 'AugStore', 'Await', 'BinOp', 'BitAnd', 'BitOr', 'BitXor', 'BoolOp', 'Break', 'Call', 
    'ClassDef', 'Compare', 'Constant', 'Continue', 'Del', 'Delete', 'Dict', 'DictComp', 'Div', 'Eq', 'ExceptHandler', 
    'Expr', 'Expression', 'ExtSlice', 'FloorDiv', 'For', 'FormattedValue', 'FunctionDef', 'FunctionType', 'GeneratorExp', 
    'Global', 'Gt', 'GtE', 'If', 'IfExp', 'Import', 'ImportFrom', 'In', 'Index', 'Interactive', 'Invert', 'Is', 'IsNot', 
    'JoinedStr', 'LShift', 'Lambda', 'List', 'ListComp', 'Load', 'Lt', 'LtE', 'MatMult', 'Match', 'MatchAs', 'MatchClass', 
    'MatchMapping', 'MatchOr', 'MatchSequence', 'MatchSingleton', 'MatchStar', 'MatchValue', 'Mod', 'Module', 'Mult', 'Name', 
    'NamedExpr', 'Nonlocal', 'Not', 'NotEq', 'NotIn', 'Or', 'Param', 'ParamSpec', 'Pass', 'Pow', 'RShift', 'Raise', 'Return', 
    'Set', 'SetComp', 'Slice', 'Starred', 'Store', 'Sub', 'Subscript', 'Suite', 'Try', 'TryStar', 'Tuple', 'TypeAlias', 
    'TypeIgnore', 'TypeVar', 'TypeVarTuple', 'UAdd', 'USub', 'UnaryOp', 'While', 'With', 'Yield', 'YieldFrom', '_ast_Ellipsis', 
    'alias', 'arg', 'arguments', 'boolop', 'cmpop', 'comprehension', 'excepthandler', 'expr', 'expr_context', 'keyword', 
    'match_case', 'mod', 'operator', 'pattern', 'slice', 'stmt', 'type_ignore', 'type_param', 'unaryop', 'withitem'
    ]


analyzer_ = {
    'Call': f'This is a function call that',
    'ClassDef': f'This is a class called',
    'Constant': f'This is literal value',
    'ExceptHandler': f'This is an exception that',
    'Expr': f'This is a function call that',
    'For': f'The for loop',
    'FunctionDef': f'This is a function called',
    'If': f'This is an if statement that',
    'Lambda': f'This is an inline function that',
    'Return': f'The function returns',
    'Try': f'This try section',
    'While': f'The while loop',
    'expr': f'This function call',
}

class AstParser:

    def __init__(self, ast: dict) -> None:
        self.ast = ast
        self._formatted = self.collect_sections(ast=ast)

    def _print_current_state(self):
        for k, v in self._formatted.items():
            print(f'{k} := {v}')

    def _handle_assignment(self, main: dict, key: dict) -> None:
        if any([True if k in ['elts', 'value'] else False for k in key['targets'][0].keys()]):
            main[key['_type'].lower()].append(key['targets'][0][list(key['targets'][0].keys())[0]])
        elif len(key['targets']) <= 1:
            main[key['_type'].lower()].append(key['targets'][0])

    def _init_section_setup(self, main: dict, ast: dict) -> dict:
        global UNHANDLED
        for key in ast['body']:
            if key['_type'].lower() in ['classdef', 'functiondef']:
                main[key['_type'].lower()].append(
                    {
                        key['name']: {}
                    }
                )

                if key['_type'].lower() == 'classdef':
                    main[key['_type'].lower()][-1][key['name']] = self.collect_sections(ast=key)

                if key['_type'].lower() == 'functiondef':
                    main[key['_type'].lower()][-1][key['name']] = self.collect_sections(ast=key)

            if key['_type'].lower() == 'assign':
                self._handle_assignment(main=main, key=key)

            if key['_type'].lower() in [
                'try', 'if', 'annassign', 'delete', 'expr', 'for', 'while', 
                'global', 'return', 'continue', 'augassign', 'with', 'raise', 
                'break', 'pass', 'assert'
                ]:
                main[key['_type'].lower()].append(key)

            if key['_type'].lower() not in HANDLED_EXPRESISONS:
                UNHANDLED.append(key['_type'].lower())
                print(key)
        return main
    
    def collect_sections(self, ast: dict, is_init: bool = True) -> dict:
        main_sections = {}
        if 'body' in ast.keys():
            for key in ast['body']:
                main_sections[key['_type'].lower()] = []

            if is_init:
                main_sections = self._init_section_setup(main=main_sections, ast=ast)
            else:
                for key in ast['body']:
                    main_sections[key['_type'].lower()].append(key)
        else:
            main_sections = ast
        return main_sections

    def handle_traversal(self, ast: Any = None, depth: int = 0, key: str = None) -> dict:
        if ast is None:
            ast = self.ast

        if isinstance(ast, dict):
            tree = self.collect_sections(ast=ast, is_init=False)
            for item, value in tree.items():
                if isinstance(value, list):
                    for branch in value:
                        self.handle_traversal(ast=branch, depth=depth+1, key=f"{key + ',' if key else ''}" + item)
                else:
                       self.switch_(key=key, params=[item, value])
        else:
            if key.split(',')[0] in ['try', 'if']:
                pass
            else:
                self._formatted[key.split(',')[0]].append(ast)
        return self._formatted
    
    def import_data(self, key: str, search: list, k: str, v: Any) -> None:
        p_list = key.split(',')
        if v is not None and str(v).lower() not in ['0', 'importfrom', 'import', 'alias']:
            if k in search and 'import' in p_list[0]:
                self._formatted[p_list[0]].append(v)
            else:
                for value in ['import', 'importfrom']:
                    if value in p_list:
                        self._formatted[p_list[p_list.index(value)]].append(v)

    def switch_(self, key: str, params: list) -> None:
         # This is for imports 
        if 'import' in key.lower():
            self.import_data(
                key=key, 
                search=['name'], 
                k=params[0],
                v=params[1]
            )

class DocumentationHandler():

    def document_code_base(self, dir_path) -> list:
        files = reader.ParseCode(path=dir_path).return_all_files(excluded=PYTHON_EXCLUDED, ext='.py')
        documents = []
        for path in files:
            ast_json_tree = reader.Converter().return_dict(ast=path.return_ast())
            parsed_doc = AstParser(ast=ast_json_tree).handle_traversal()
            parsed_doc['file_name'] = path.name
            documents.append(parsed_doc)

        return documents
    
    def document_file(self, file_path: str) -> dict:
        ast_json_tree = reader.Converter().return_dict(ast=reader.ParseCode(path=file_path).return_ast())
        parsed_doc = AstParser(ast=ast_json_tree).handle_traversal()
        parsed_doc['file_name'] = file_path.split('/')[-1].replace('.py', '')
        return parsed_doc

    def document_file_list(self, list_of_paths: list)-> list:
        documents = []
        for path in list_of_paths:
            ast_json_tree = reader.Converter().return_dict(ast=reader.ParseCode(path=path).return_ast())
            parsed_doc = AstParser(ast=ast_json_tree).handle_traversal()
            parsed_doc['file_name'] = path.split('/')[-1].replace('.py', '')
            documents.append(parsed_doc)
        
        return documents
    
class DocumentGenerator:

    def __init__(self, folder_name: str = 'Generic_Docs'):
        self.name = folder_name
        path = Path(folder_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        _name = "wizardlm-13b-v1.2.Q4_0.gguf"
        self.model = GPT4All(_name, device='cpu')

    def describe_ast_nodes(self, ast_dict, section: str, analyzer_: dict = analyzer_) -> str:
        descriptions = []

        def describe_node(node):
            if isinstance(node, dict):
                node_type = node.get('_type')
                description = analyzer_.get(node_type)
                if description:
                    name = node.get('name') or node.get('id') or node.get('value') or node.get('func') or len(node)
                    descriptions.append(f'{description} {name} \n')
                for value in node.values():
                    describe_node(value)
            elif isinstance(node, list):
                for item in node:
                    describe_node(item)

        describe_node(ast_dict)
        documented = list()
        for chunk in descriptions:
            doc = self.gpt(section=chunk, section_name=section) + '\n'
            documented.append(doc)
            print(doc)

        return ' '.join(documented)
        

    def gpt(self, section: str, section_name: str) -> str:
        global HANDLED_EXPRESISONS
        _query =  f"Please analyze this small ast subsection in the {section_name} section and write documentation for it: {section}"
        res = self.model.generate(_query, max_tokens=2048)
        return res


    def stringify_section(self, section: list, section_name: str) ->str:
        document = ''
        for item in section:
            if isinstance(item, dict):
                document += self.describe_ast_nodes(ast_dict=item, section=section_name) + '\n\n'
            elif isinstance(item, list):
                for node in item:
                    document += self.describe_ast_nodes(ast_dict=node, section=section_name) + '\n\n'
            else:
                document += item + '\n'

        return document

    def output_generic_doc(self, file: IO, doc: dict):
        for section, s_value in doc.items():
            file.write(f'# {section.title()} \n')
            file.write(self.stringify_section(section=s_value, section_name=section))
            file.write('\n\n')

    def create_document(self, docs: Union[list, dict]) -> str:
        if isinstance(docs, list):
            for doc in docs:
                name = doc.pop('file_name')
                print(f'Currently Documenting {name}')
                with open(f'{self.name}/{name}_doc.md', 'w+') as o_file:
                    self.output_generic_doc(file=o_file, doc=doc)

        else:
            name = docs.pop('file_name')
            with open(f'{self.name}/{name}_doc.md', 'w+') as o_file:
                    self.output_generic_doc(file=o_file, doc=docs)
