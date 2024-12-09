import sys
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from loguru import logger

sys.path.extend(['.', '..'])

from configuration import *

parser = Parser(Language(tsjava.language()))


def syntax_check(test_class: str) -> bool:
    try:
        tree = parser.parse(bytes(test_class, "utf-8"))
        return not tree.root_node.has_error
    except:
        return False


def modify_generated_class(test_class: str) -> str:
    test_class = add_package_declaration(test_class)
    test_class = change_class_name(test_class)
    return test_class


def change_class_name(test_class: str) -> str:
    origin_class_bytes = bytes(test_class, 'utf-8')
    tree = parser.parse(origin_class_bytes)
    class_decl_cand = [n for n in tree.root_node.children if n.type == 'class_declaration']

    public_class_decl_node = None
    for candidate in class_decl_cand:
        for child in candidate.children:
            if child.type == 'modifiers':
                if any([c.type == 'public' for c in child.children]):
                    # 应该只有一个 public class，所以直接 break
                    public_class_decl_node = candidate
                    break
    if not public_class_decl_node:
        logger.warning(f'No public class defined, continue.')
        logger.info(f'{test_class}')
        return test_class
    else:
        class_name_node = public_class_decl_node.child_by_field_name('name')
        new_class_bytes = origin_class_bytes[:class_name_node.start_byte] + 'LLMTests'.encode(
            'utf-8') + origin_class_bytes[class_name_node.end_byte + 1:]
        return new_class_bytes.decode('utf-8')


def add_package_declaration(test_class: str) -> str:
    tree = parser.parse(bytes(test_class, 'utf-8'))
    if tree.root_node.children[0].type == 'package_declaration':
        new_test_class = 'package org.llm;\n'.encode('utf-8') + bytes(test_class, 'utf-8')[
                                                                tree.root_node.children[0].end_byte:]
        return new_test_class.decode('utf-8')
    else:
        return 'package org.llm;\n\n' + test_class


def parse_imports_from_file(file_content: str) -> list[str]:
    tree = parser.parse(bytes(file_content, 'utf-8'))
    package_decl_nodes = [n for n in tree.root_node.children if n.type == 'package_declaration']
    package_import = None
    if len(package_decl_nodes) >= 1:
        package_decl_node = package_decl_nodes[0]
        package_import = f"import {package_decl_node.child(1).text.decode('utf-8')}.*;"

    import_decl_nodes = [n for n in tree.root_node.children if n.type == 'import_declaration']
    imports = [package_import] if package_import else []
    for import_decl_node in import_decl_nodes:
        imports.append(import_decl_node.text.decode('utf-8'))
    return imports


def add_imports(test_class: str, imports: list) -> str:
    origin_class_byte = bytes(test_class, 'utf-8')
    tree = parser.parse(origin_class_byte)
    final_import_node = None
    for node in tree.root_node.children:
        if node.type == 'import_declaration':
            final_import_node = node
    if not final_import_node:
        logger.warning('no imports defined in the class')
        return test_class
    else:
        new_test_class = origin_class_byte[:final_import_node.end_byte] + \
                         ('\n' + '\n'.join(imports) + '\n').encode('utf-8') + \
                         ('\n'+'\n'.join(pre_defined_imports)+'\n').encode('utf-8') + \
                         origin_class_byte[final_import_node.end_byte + 1:]
        return new_test_class.decode('utf-8')
