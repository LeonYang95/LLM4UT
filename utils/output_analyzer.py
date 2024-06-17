import os
import os
import pickle
import re

import javalang
import javalang.tree

from data.configuration import d4j_proj_base
from utils.d4j_utils import assemble_test_class, content_path, _get_src_location_by_bug_id
from utils.java_parser import (
    parse_import_stmts_from_file_code,
    parse_methods_from_class_node,
    parse_fields_from_class_code,
    parse_classes_from_file_node,
    parse_method_invocation,
    parse_methods_from_class_node_no_deduplication
)
junit_imports=[
    "import org.junit.Test;",
    "import org.junit.Assert;",
    "import org.junit.Before;",
    "import org.junit.After;",
    "import static org.junit.Assert.*;",
    "import org.junit.Ignore;",
    "import org.junit.BeforeClass;",
    "import org.junit.AfterClass;",
    "import org.junit.runner.RunWith;",
    "import org.junit.runners.JUnit4;",
    "import org.junit.Rule;",
    "import org.junit.rules.ExpectedException;",
    "import static org.mockito.Mockito.*;",
    "import org.mockito.Mockito;",
]
focal_imports = [
    "import org.junit.Test;",
    "import org.junit.Assert;",
    "import org.junit.Before;",
    "import org.junit.After;",
    "import static org.junit.Assert.*;",
    "import org.junit.Ignore;",
    "import org.junit.BeforeClass;",
    "import org.junit.AfterClass;",
    "import org.junit.runner.RunWith;",
    "import org.junit.runners.JUnit4;",
    "import org.junit.Rule;",
    "import org.junit.rules.ExpectedException;",
    "import static org.mockito.Mockito.*;",
    "import org.mockito.Mockito;",
    "import static org.hamcrest.MatcherAssert.assertThat;",
    "import static org.hamcrest.Matchers.*;",
    "import java.text.SimpleDateFormat;",
    "import java.io.*;",
    "import java.lang.*;",
    "import java.util.*;",
    "import java.time.*;",
    "import java.math.*;",
    "import java.net.*;",
    "import java.security.*;",
    "import java.nio.file.Files;",
    "import java.nio.file.Path;",
]


def extract_method_name(method_code):
    # Parse the Java code
    method_code = "public class TmpClass {\n" + method_code + "}\n"
    tree = javalang.parse.parse(method_code)

    method_names = []
    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        method_names.append(node.name)
    return method_names[0]


def contains_focal_method_invocation(method_str, target_signature):
    pattern = re.compile(r"\(.*?\)")
    tmp_signature = pattern.sub("#", target_signature)
    tks = tmp_signature.split("#")
    method_name = tks[2]
    invocations = parse_method_invocation(method_str)
    for invocation in invocations:
        if invocation["invoked_method_name"] == method_name:
            return True
    return False


def analyze_outputs(output_str: str, strategy: str, method_signature=None):
    block_dot_lines = []
    lines = output_str.split("\n")
    if strategy == "generation":
        for id, line in enumerate(lines):
            if line.startswith("```"):
                block_dot_lines.append(id)
    elif strategy == "extend":
        for id, line in enumerate(lines):
            if line.endswith("```") or line.startswith("```"):
                block_dot_lines.append(id)
                pass
            else:
                pass
        pass
    else:
        raise NotImplementedError(
            f"Strategy {strategy} is not supported for analyze_outputs method"
        )
    total_lines = len(lines)
    methods = []
    imports = []
    fields = []
    classes = []
    start = 0
    for id in block_dot_lines:
        if id == 0:
            start = 1
            continue
        cur_block = lines[start: id]
        cur_content = "\n".join(cur_block)
        if lines[id].startswith("```"):
            pass
        else:
            column_id = lines[id].find("```")
            if column_id == -1:
                raise IndexError(f"Failing in finding ``` starters in {lines[id]}")
            else:
                cur_content += lines[id][:column_id]

        # methods.extend(parse_methods_from_class_node(cur_content, strategy))
        if method_signature is not None:
            raw_methods = parse_methods_from_class_node(cur_content)
            for candidate in raw_methods:
                modifier = candidate["method_modifiers"]
                if "@Test" in modifier:
                    if contains_focal_method_invocation(
                            candidate["method_text"], method_signature
                    ):
                        methods.append(
                            pickle.loads(pickle.dumps(candidate["method_text"]))
                        )
                    else:
                        continue
                else:
                    methods.append(pickle.loads(pickle.dumps(candidate["method_text"])))
            pass
        else:
            methods.extend(
                [i["method_text"] for i in parse_methods_from_class_node(cur_content)]
            )
        imports.extend(parse_import_stmts_from_file_code(cur_content))
        # fields.extend(parse_fields_from_class_code(cur_content, strategy))
        fields.extend(
            [i["declaration_text"] for i in parse_fields_from_class_code(cur_content)]
        )
        classes.extend(parse_classes_from_file_node(cur_content, strategy))
        start = id + 1
        pass

    if start < total_lines:
        if start == 0:
            pass
        else:
            start += 1
        cur_block = lines[start:]
        cur_content = "\n".join(cur_block)
        cur_methods = parse_methods_from_class_node(cur_content)
        if len(cur_methods) != 0:
            # methods.extend(cur_methods)
            # methods.extend([i["method_text"] for i in cur_methods])
            if method_signature is not None:
                raw_methods = parse_methods_from_class_node(cur_content)
                for candidate in raw_methods:
                    modifier = candidate["method_modifiers"]
                    if "@Test" in modifier:
                        if contains_focal_method_invocation(
                                candidate["method_text"], method_signature
                        ):
                            methods.append(
                                pickle.loads(pickle.dumps(candidate["method_text"]))
                            )
                        else:
                            continue
                    else:
                        methods.append(
                            pickle.loads(pickle.dumps(candidate["method_text"]))
                        )
                pass
            else:
                methods.extend(
                    [
                        i["method_text"]
                        for i in parse_methods_from_class_node(cur_content)
                    ]
                )
            imports.extend(parse_import_stmts_from_file_code(cur_content))
            fields.extend(
                [
                    i["declaration_text"]
                    for i in parse_fields_from_class_code(cur_content)
                ]
            )
            classes.extend(parse_classes_from_file_node(cur_content))

    imports = list(set(imports))
    methods = set(methods)
    fields = list(set(fields))

    return methods, imports, fields, classes

def summarize_uts_no_deduplication(output_str: str, strategy: str, method_signature=None):
    block_dot_lines = []
    lines = output_str.split("\n")
    if strategy == "generation":
        for id, line in enumerate(lines):
            if line.startswith("```"):
                block_dot_lines.append(id)
    elif strategy == "extend":
        for id, line in enumerate(lines):
            if line.endswith("```") or line.startswith("```"):
                block_dot_lines.append(id)
                pass
            else:
                pass
        pass
    else:
        raise NotImplementedError(
            f"Strategy {strategy} is not supported for analyze_outputs method"
        )
    total_lines = len(lines)
    methods = []
    imports = []
    fields = []
    classes = []
    start = 0
    for id in block_dot_lines:
        if id == 0:
            start = 1
            continue
        cur_block = lines[start: id]
        cur_content = "\n".join(cur_block)
        if lines[id].startswith("```"):
            pass
        else:
            column_id = lines[id].find("```")
            if column_id == -1:
                raise IndexError(f"Failing in finding ``` starters in {lines[id]}")
            else:
                cur_content += lines[id][:column_id]

        # methods.extend(parse_methods_from_class_node(cur_content, strategy))
        methods.extend(
            [i["method_text"] for i in parse_methods_from_class_node_no_deduplication(cur_content)]
        )
        imports.extend(parse_import_stmts_from_file_code(cur_content))
        # fields.extend(parse_fields_from_class_code(cur_content, strategy))
        fields.extend(
            [i["declaration_text"] for i in parse_fields_from_class_code(cur_content)]
        )
        classes.extend(parse_classes_from_file_node(cur_content, strategy))
        start = id + 1
        pass

    if start < total_lines:
        if start == 0:
            pass
        else:
            start += 1
        cur_block = lines[start:]
        cur_content = "\n".join(cur_block)
        cur_methods = parse_methods_from_class_node_no_deduplication(cur_content)
        if len(cur_methods) != 0:
            # methods.extend(cur_methods)
            # methods.extend([i["method_text"] for i in cur_methods])
            methods.extend(
                [
                    i["method_text"]
                    for i in parse_methods_from_class_node_no_deduplication(cur_content)
                ]
            )
            imports.extend(parse_import_stmts_from_file_code(cur_content))
            fields.extend(
                [
                    i["declaration_text"]
                    for i in parse_fields_from_class_code(cur_content)
                ]
            )
            classes.extend(parse_classes_from_file_node(cur_content))

    imports = list(set(imports))
    methods = set(methods)
    fields = list(set(fields))

    return methods, imports, fields, classes


def assemble_first_round_test_class(
        project_name,
        class_sig,
        imports,
        methods,
        fields,
        import_json,
        classes,
):
    """
    Assembles the first round test class.

    Args:
        project_name (str): The name of the project.
        class_sig (str): The signature of the class.
        imports (list): The list of imports.
        methods (list): The list of methods.
        fields (list): The list of fields.
        import_json (dict): The import JSON.
        classes (list): The list of classes.

    Returns:
        str: The assembled test class.
    """

    package_name = ".".join(class_sig.split(".")[:-1])
    focal_base_dir, _ = _get_src_location_by_bug_id(project_name)
    focal_class_file = class_sig.replace(".", "/") + ".java"
    focal_class_import = []
    if "Gson" in project_name or "Csv" in project_name:
        pass
    else:
        with open(
                os.path.join(focal_base_dir, focal_class_file),
                "r",
                encoding="iso8859-1",
        ) as f:
            focal_content = f.read()
        focal_class_import.extend(parse_import_stmts_from_file_code(focal_content))

    imports.append(f"import {class_sig};")
    # 根据LLM生成的 imports ，酌情加入imports
    # remove enum to avoid java version isse
    focal_class_import = [i for i in focal_class_import if "enum" not in i.split(".")]
    pre_defined_imports = [i for i in focal_imports if "enum" not in i.split(".")]
    import_list = pickle.loads(
        pickle.dumps(import_json[project_name]["fixed"])
    )  # 按src得到的imports
    src_imports = [i for i in import_list if "enum" not in i.split(".")]
    llm_imp_set = set(imports)
    focal_class_import = filter_imports(focal_class_import, llm_imp_set)
    pre_defined_imports = filter_imports(
        pre_defined_imports, set(focal_class_import) | llm_imp_set
    )
    src_imports = filter_imports(
        src_imports, llm_imp_set | set(focal_class_import) | set(pre_defined_imports)
    )

    class_declaration = "public class LLMGeneratedTests {"

    current_method_names = {}
    new_methods = []
    for method in methods:
        try:
            method_name = extract_method_name(method)
            if method_name in current_method_names.keys():
                current_method_names[method_name] = (
                        current_method_names[method_name] + 1
                )
                method = method.replace(
                    method_name, method_name + str(current_method_names[method_name])
                )
            else:
                current_method_names[method_name] = 0
            new_methods.append(method)
        except:
            continue

    assembled_test_class = assemble_test_class(
        package_name,
        imports,
        focal_class_import,
        src_imports,
        pre_defined_imports,
        class_declaration,
        new_methods,
        fields,
        classes,
    )
    return assembled_test_class, package_name + ".LLMGeneratedTests"


def assemble_recursive_test_classes(
        package_name,
        imports,
        methods,
        fields,
        classes,
):
    class_declaration = "public class LLMGeneratedTests {"
    current_method_names = {}
    new_methods = []
    for method in methods:
        try:
            method_name = extract_method_name(method)
            if method_name in current_method_names.keys():
                current_method_names[method_name] = (
                        current_method_names[method_name] + 1
                )
                method = method.replace(
                    method_name, method_name + str(current_method_names[method_name])
                )
            else:
                current_method_names[method_name] = 0
            new_methods.append(method)
        except:
            continue

    assembled_test_class = assemble_test_class(
        package_name,
        [],
        [],
        [],
        imports,
        class_declaration,
        new_methods,
        fields,
        classes,
    )

    return assembled_test_class, package_name + ".LLMGeneratedTests"


def _get_test_class_path(bug_id, version, class_sig):
    """
    Get the test class path for a given bug ID, version, and focal class.

    Args:
        bug_id (str): The ID of the bug.
        version (str): The version of the bug.
        focal_class (str): The focal class.

    Returns:
        tuple: A tuple containing the test file directory, the resulting file path, the class declaration, and the test class name.
    """

    if content_path[bug_id.lower()]["test"][0] != "/":
        test_base = content_path[bug_id.lower()]["test"]
    else:
        test_base = content_path[bug_id.lower()]["test"][1:]
    test_base_dir = os.path.join(d4j_proj_base, bug_id, version, test_base)

    # 找到测试文件具体应该在的子目录
    test_class_dir = "/".join(class_sig.split(".")[:-1])
    test_file_dir = os.path.join(str(test_base_dir), test_class_dir)
    test_class_name = class_sig.split(".")[-1]
    class_declaration = "public class " + test_class_name + "{"
    # 指定测试文件的路径
    res_file_path = os.path.join(str(test_file_dir), test_class_name + ".java")

    return test_file_dir, res_file_path, class_declaration, test_class_name


def assemble_empty_test_file():
    """
    Assembles an empty test file.

    Returns:
        tuple: A tuple containing the new content of the test file and the fully qualified name of the test class.
    """
    new_content = f"package org.llm.gen.tests;\n import org.junit.Test;\nimport static org.junit.Assert.assertTrue;\npublic class EmptyTests{{\n    @Test\n    public void emptyTest(){{\n        assertTrue(true);\n    }}\n}}\n"
    return new_content, "org.llm.gen.tests.EmptyTests"


def write_test_file(bug_id, version, class_sig, content):
    """
    Write the content to a test file for a specific bug, version, and focal class.

    Parameters:
    bug_id (str): The ID of the bug.
    version (str): The version of the software.
    focal_class (str): The name of the focal class.
    content (str): The content to be written to the test file.
    """
    test_file_dir, test_file_path, _, _ = _get_test_class_path(
        bug_id, version, class_sig
    )
    if not os.path.exists(test_file_dir):
        os.makedirs(test_file_dir)
    with open(test_file_path, "w", encoding="utf-8") as writer:
        writer.write(content)

    pass


def delete_test_file(bug_id, version, class_sig):
    test_file_dir, test_file_path, _, _ = _get_test_class_path(
        bug_id, version, class_sig
    )
    if os.path.exists(test_file_path):
        os.system(f"rm -f {test_file_path}")
    pass


def clear_test_file(bug_id, class_sig):
    """
    Clears the test file directory for a given bug ID and class signature.

    Args:
        bug_id (str): The ID of the bug.
        class_sig (str): The signature of the class.

    Returns:
        None
    """
    test_file_dir, _, _, _ = _get_test_class_path(bug_id, "fixed", class_sig)
    if os.path.exists(test_file_dir):
        os.system(f"rm -rf {test_file_dir}")


def filter_imports(src_imports: list, tgt_imports: set):
    """
    filter imports from source list from target list.
    :param src_imports: source import list, which is about to be merged.
    :param tgt_imports: target import list, which is the imports that generated by LLM
    :return: merged import set
    """

    # find all classes that are imported by target import statements
    classes_imported_by_tgt = []
    packages_imported_by_tgt = []
    final_imports = []
    jupiters_included_in_tgt = False
    for import_str in tgt_imports:
        tokens = import_str.split()
        if len(tokens) == 2 and tokens[0] == "import":
            cls_str = tokens[1].split(".")[-1][:-1]
            if "org.junit.jupiter" in tokens[1]:
                jupiters_included_in_tgt = True
            if cls_str == "*":
                packages_imported_by_tgt.append(".".join(tokens[1].split(".")[:-1]))
                pass
            else:
                classes_imported_by_tgt.append(cls_str)
            # final_imports.append(import_str)
            pass
        elif len(tokens) == 3 and tokens[0] == "import" and tokens[1] == "static":
            cls_str = tokens[2].split(".")[-1][:-1]
            if "org.junit.jupiter" in tokens[2]:
                jupiters_included_in_tgt = True
            if cls_str == "*":
                packages_imported_by_tgt.append(".".join(tokens[2].split(".")[:-1]))
                pass
            else:
                classes_imported_by_tgt.append(cls_str)
            # final_imports.append(import_str)
            pass
        else:
            raise NotImplementedError(
                f"more than 3 tokens in {import_str}, please check"
            )

    for import_str in src_imports:
        tokens = import_str.split()
        if len(tokens) == 2 and tokens[0] == "import":
            cls_str = tokens[1].split(".")[-1][:-1]
            imported_cls = tokens[1]
            pass
        elif len(tokens) == 3 and tokens[0] == "import" and tokens[1] == "static":
            cls_str = tokens[2].split(".")[-1][:-1]
            imported_cls = tokens[2]
            pass
        else:
            raise NotImplementedError(
                f"more than 3 tokens in {import_str}, please check"
            )

        if cls_str in classes_imported_by_tgt:
            # 同名的去掉
            continue

        # 去掉Assert 和 junit.jupiter.Assertion的问题
        # org.junit.jupiter.api.Assertions.*

        package_name = ".".join(imported_cls.split(".")[:-1])
        if (package_name in packages_imported_by_tgt) or (
                package_name.startswith("org.junit") and jupiters_included_in_tgt
        ):
            # 如果已经引入*，则不需要继续补充
            continue

        final_imports.append(import_str)

    return final_imports
