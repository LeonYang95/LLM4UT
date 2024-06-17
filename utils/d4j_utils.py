import sys

sys.path.extend([".", ".."])
import os
import io
import json
import re
import signal
import subprocess
import pickle
import xml.etree.ElementTree as ET

from tqdm import tqdm
from collections import Counter, defaultdict

from utils.exceptions import *
from data.configuration import d4j_proj_base, code_base, d4j_command
from utils.java_parser import (
    parse_import_stmts_from_file_code,
    parse_methods_from_class_node,
    parse_fields_from_class_code,
    parse_superclass_or_interface_from_class_node
)

# 加载对应项目的src和test的路径
with open(os.path.join(code_base, "data/test_src.json"), "r") as f:
    content_path = json.load(f)


def _get_test_location_by_bug_id(bug_id):
    fixed_base = content_path[bug_id.lower()]["test"]
    buggy_base = content_path[bug_id.lower()]["test"]
    fixed_base = os.path.join(d4j_proj_base, bug_id, "fixed", fixed_base)
    buggy_base = os.path.join(d4j_proj_base, bug_id, "buggy", buggy_base)
    return fixed_base, buggy_base


def _get_src_location_by_bug_id(bug_id):
    fixed_base = content_path[bug_id.lower()]["src"]
    buggy_base = content_path[bug_id.lower()]["src"][1:]
    fixed_base = os.path.join(d4j_proj_base, bug_id, "fixed", fixed_base)
    buggy_base = os.path.join(d4j_proj_base, bug_id, "buggy", buggy_base)
    return fixed_base, buggy_base


pre_defined_imports = [
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

with open(
        os.path.join(code_base, "data/test_src.json"), "r", encoding="utf-8"
) as reader:
    test_src = json.load(reader)


def load_assistant_data():
    """
    加载辅助文件，配合数据分析

    Returns:
        list: 辅助数据的列表
    """
    assistant_datas = []
    assistant_prompt_file = os.path.join(code_base, "data/d4j_assistant.jsonl")
    with open(assistant_prompt_file, "r", encoding="utf-8") as reader:
        for line in tqdm(reader.readlines(), desc="Reading assistant prompt file :"):
            line = line.strip()
            data = json.loads(line)
            # if data['project'] == target_project:
            assistant_datas.append(pickle.loads(pickle.dumps(data)))

    return assistant_datas


def load_assistant_data_with_shell():
    assistant_datas = []
    assis_file_with_shell = os.path.join(code_base, "data/d4j_assistant_with_shell.jsonl")
    assis_file = os.path.join(code_base, "data/d4j_assistant.jsonl")
    with open(assis_file, "r", encoding="utf-8") as reader:
        with open(assis_file_with_shell, 'r', encoding='utf-8') as shell_reader:
            for line in tqdm(reader.readlines(), desc="Reading assistant prompt file :"):
                line = line.strip()
                data = json.loads(line)
                data_with_shell = json.loads(shell_reader.readline().strip())
                assert data['focal_method'] == data_with_shell['source:source_method_code_format']
                data['test_shell'] = data_with_shell['test_shell'].split('_')[0]
                data['method_signature'] = data_with_shell['source:source_method_signature']
                assistant_datas.append(pickle.loads(pickle.dumps(data)))
    return assistant_datas


def find_test_class(bug_id: str, focal_class: str, dpo_extension=False):
    """
    find source class file and test class file for given bug id and focal class

    Args:
        bug_id (str): bug id in defects4j benchmark
        focal_class (str): the targeted class

    Returns:
        tuple of strings or None: tuple of source class file and test class file, test class file could be None. And if both files are not found, return None.
    """
    base_folder = os.path.join(d4j_proj_base, bug_id, "fixed")
    tks = focal_class.split(".")
    pkg_path = "/".join(tks[:-1])
    class_name = tks[-1]

    src_base = test_src[bug_id.lower()]["src"]
    test_base = test_src[bug_id.lower()]["test"]

    src_folder = os.path.join(base_folder, src_base, pkg_path)
    test_folder = os.path.join(base_folder, test_base, pkg_path)
    if os.path.exists(src_folder):
        src_file = os.path.join(src_folder, class_name + ".java")
        if not os.path.exists(src_file):
            raise FileNotFoundError(f"source file {src_file} not found.")

        test_file = None
        if os.path.exists(test_folder):
            for root, _, files in os.walk(test_folder):
                for file in files:
                    if file.endswith(".java") and class_name in file:
                        test_file = os.path.join(root, file)
                        break
        else:
            if dpo_extension:
                for root, _, files in os.walk(os.path.join(base_folder,test_base)):
                    for file in files:
                        if file.endswith(".java") and class_name in file:
                            test_file = os.path.join(root, file)
                            break

        return src_file, test_file
    else:
        raise FileNotFoundError(f"source folder {src_folder} not found.")


def convert_imports_to_paths_and_packages(import_statements):
    """
    Converts a list of Java import statements to file paths and package paths,
    considering both regular and static imports.

    Args:
    import_statements (list of str): List of import statements from a Java file.

    Returns:
    list of tuples: Each tuple contains the package path and corresponding file path.
    """
    paths_and_packages = []
    for statement in import_statements:
        is_static = statement.startswith("import static ")
        prefix = "import static " if is_static else "import "

        # Remove 'import ' or 'import static ' prefix and ';' suffix
        path = statement.replace(prefix, "").rstrip(";")

        if is_static:
            # For static imports, remove the static member (last part after the last dot)
            package_path = ".".join(path.split(".")[:-1])
        else:
            # For regular imports, the package path is everything except the class name
            package_path = ".".join(path.split(".")[:-1])

        # Convert package path to file path and add '.java'
        file_path = package_path.replace(".", "/") + "/" + path.split(".")[-1] + ".java"
        paths_and_packages.append((package_path, file_path))

    return paths_and_packages


def load_src_imports(bug_id: str, src_file: str):
    """
    从source文件中加载public的import语句

    Args:
        bug_id (str): bug id in defects4j benchmark
        src_file (str): source 文件

    Raises:
        NotImplementedError: 如果出现import语句中的token超过3个（一般来说只有import （static）org.junit.Assert.assertEquals;），超过这个数量就抛出NotImplementedError

    Returns:
        list: 过滤出来的import语句
    """
    ret = set()
    with open(src_file, "r", encoding="iso8859-1") as reader:
        src = reader.read()

    # 找到src file所属的package，为了后面引入同名package下的其他类做准备
    package_name = ""
    for line in src.split("\n"):
        if line.strip().startswith("package"):
            package_name = line.replace("package ", "")
            package_name = package_name.rstrip(";").strip()
            break

    imports = parse_import_stmts_from_file_code(src)
    paths = convert_imports_to_paths_and_packages(imports)

    base_folder = os.path.join(d4j_proj_base, bug_id, "fixed")
    src_base = test_src[bug_id.lower()]["src"]
    src_base = os.path.join(base_folder, src_base)

    for (pkg_path, file_path), imp_str in zip(paths, imports):
        if os.path.exists(os.path.join(src_base, file_path)):
            # 如果这个同名文件能够找到，那么这个类应该是public的，应该可以导入
            ret.add(imp_str)
            pass
        else:
            if not os.path.exists(os.path.join(src_base, pkg_path)):
                # 如果这个包名没有找到，那么说明可能是第三方的调用（因为默认不会在项目中导入不存在的类）
                ret.add(imp_str)
                pass

    # 最后导入src所属的package，因为可能会有同包的类，没有显式的导入
    if package_name != "":
        ret.add(f"import {package_name}.*;")

    return list(ret)


def load_test_imports(bug_id: str, test_file: str):
    """
    从test文件中加载public的import语句

    Args:
        bug_id (str): bug id in defects4j benchmark
        src_file (str): source 文件

    Raises:
        NotImplementedError: 如果出现import语句中的token超过3个（一般来说只有import （static）org.junit.Assert.assertEquals;），超过这个数量就抛出NotImplementedError

    Returns:
        list: 过滤出来的import语句
    """
    ret = set()
    with open(test_file, "r", encoding="iso8859-1") as reader:
        content = reader.read()

    imports = parse_import_stmts_from_file_code(content)
    paths = convert_imports_to_paths_and_packages(imports)

    base_folder = os.path.join(d4j_proj_base, bug_id, "fixed")

    test_base = test_src[bug_id.lower()]["test"]
    test_base = os.path.join(base_folder, test_base)

    src_base = test_src[bug_id.lower()]["src"]
    src_base = os.path.join(base_folder, src_base)

    for (pkg_path, file_path), imp_str in zip(paths, imports):
        ret.add(imp_str)
        # if os.path.exists(os.path.join(src_base, file_path)):
        #     # 如果这个同名文件能够找到，那么这个类应该是public的，应该可以导入
        #     ret.add(imp_str)
        #     pass
        # else:
        #     if (
        #             not os.path.exists(os.path.join(src_base, pkg_path))
        #             and "junit.framework" not in imp_str
        #             and (not os.path.exists(os.path.join(test_base, file_path)))
        #     ):
        #         # 如果这个包名没有找到，那么说明可能是第三方的调用（因为默认不会在项目中导入不存在的类
        #         # 这里还要去掉junit.framework的依赖，因为这个是junit3的，模型基本都是junit4起步
        #         # 这里还要去掉其他测试类，如果这个import的类在test文件夹内能够找到，则不需要加入
        #         ret.add(imp_str)
        #         pass

    return list(ret)


def load_setup_methods(test_class: str):
    ret = []
    methods = parse_methods_from_class_node(test_class, need_prefix=False)
    for method in methods:
        if method["method_modifiers"] != "":
            modifiers = [
                x.strip() for x in method["method_modifiers"].split() if x != ""
            ]
            add = True
            for modifier in modifiers:
                if '@Test' in modifier:
                    add = False
                    break
            if add:
                ret.append(method)
        else:
            ret.append(method)
            pass
    return ret


def assemble_test_class(
        package_name: str,
        imports,
        focal_class_import: list,
        src_imports: list,
        pre_defined_imports: list,
        class_declaration: str,
        new_methods: list,
        fields: list,
        classes: list,
):
    """
    Assembles a test class with the given parameters.

    Args:
        package_name (str): The name of the package.
        imports: The imports required for the test class.
        focal_class_import (list): The imports from the focal class.
        src_imports (list): The imports from the source.
        pre_defined_imports (list): The pre-defined imports.
        class_declaration (str): The declaration of the class.
        new_methods (list): The new methods to be added to the class.
        fields (list): The fields to be added to the class.
        classes (list): The additional classes to be added to the class.

    Returns:
        str: The assembled test class.
    """
    res_content = ""
    res_stream = io.StringIO(res_content)
    res_stream.write(f"package {package_name};\n")

    res_stream.write("// from focal class\n")
    for imp in focal_class_import:
        res_stream.write(imp + "\n")

    res_stream.write("\n// from src\n")
    for imp in src_imports:
        res_stream.write(imp + "\n")

    res_stream.write("\n// from LLM\n")
    for imp in imports:
        res_stream.write(imp + "\n")

    res_stream.write("\n// pre-defined\n")
    for imp in pre_defined_imports:
        res_stream.write(imp + "\n")

    res_stream.write("\n")
    res_stream.write(class_declaration + "\n")
    res_stream.write("\n")

    for field in fields:
        res_stream.write(field + "\n")

    for method in new_methods:
        res_stream.write("\n" + method + "\n")
        res_stream.write("\n")

    res_stream.write("}")

    for single_class in classes:
        if is_static_class(single_class):
            continue
        res_stream.write(f"\n{single_class}\n")

    assembled_test_class = res_stream.getvalue()
    return assembled_test_class


def is_static_class(class_content):
    if "static class" in class_content:
        return True
    else:
        return False


def summarize_d4j_test_shell():
    """
    为SFT之后的模型准备prompt时，提供测试类的壳
    """
    data = []
    with open(
            os.path.join(code_base, "data/prompts/source_data.jsonl"), "r", encoding="utf-8"
    ) as reader:
        for line in reader.readlines():
            data.append(json.loads(line.strip()))

    test_file_not_found = 0
    has_setup = 0
    test_folder_not_found = 0
    bugs_has_setup = set()
    total = 0
    writer = open(
        os.path.join(code_base, "data/d4j_assistant_with_shell.jsonl"),
        "w",
        encoding="utf-8",
    )
    for index, inst in tqdm(enumerate(data), desc=f"Summarizing test shells"):
        class_sig = inst["source:source_method_signature"]
        pkg, class_name = class_sig.split("#")[0:2]
        class_sig = ".".join([pkg, class_name])
        package_decl = f"package {pkg};"
        bug_id = inst["extra:project_name"][:-6]
        total += 1
        has_superclass_or_interfaces = 0
        res = find_test_class(bug_id, class_sig)
        src_file, test_file = res
        src_imports = load_src_imports(bug_id=bug_id, src_file=src_file)

        if test_file is None:
            test_file_not_found += 1
            test_imports = [f"import {class_sig};", f"import {pkg}.*;"]
            methods = []
            fields = []
            superclasses = []
            interfaces = []
        else:
            with open(test_file, "r", encoding="iso8859-1") as f:
                content = f.read()

            test_imports = load_test_imports(bug_id=bug_id, test_file=test_file)
            methods = load_setup_methods(content)
            fields = parse_fields_from_class_code(content, need_prefix=False)
            tmp = parse_superclass_or_interface_from_class_node(content)
            superclasses = tmp['superclasses'][0] if tmp['superclasses'] else ''
            interfaces = tmp['interfaces'][0] if tmp['interfaces'] else ''
            if len(methods) != 0:
                has_setup += 1
                bugs_has_setup.add(bug_id)

        imports = set(pre_defined_imports + src_imports + test_imports)
        import_decl = "\n".join(imports)
        header = f"{package_decl}\n{import_decl}\n"
        postfix = ''

        if 'TestCase' in superclasses:
            methods = []
            superclasses = ''
            has_setup -=1

        if len(superclasses) != 0:
            postfix += superclasses
        if len(interfaces) != 0:
            postfix += f" {interfaces}"

        class_declaration = f"public class LLMGeneratedTests {postfix} {{\n"
        header += f"public class LLMGeneratedTests {postfix} {{\n\t"
        field_decl = "\n".join([field["declaration_text"] for field in fields])
        method_decl = "\n".join([method["method_text"] for method in methods])
        header += field_decl + "\n" + method_decl + "\n"
        inst["test_shell"] = header
        inst['class_declaration'] = class_declaration
        output_str = json.dumps(inst)
        try:
            tmp = json.loads(output_str)
        except Exception:
            raise Exception("blabla")
        writer.write(json.dumps(inst) + "\n")

    # writer.close()

    print(f"test file not found: {test_file_not_found}")
    print(f"test folder not found: {test_folder_not_found}")
    print(has_setup)
    print(bugs_has_setup)
    print(total)


def _compile_and_collect_results(root):
    """
    进行d4j compile过程，并且收集编译结果

    Args:
        root (str): 运行命令的根目录

    Returns:
        compile_flag (str): 表示编译成功，0表示编译失败
        compile_error_msg (str): 编译错误的terminal输出
        compile_error_reasons (Counter): 编译错误的原因

    """
    cur_dir = os.getcwd()
    os.chdir(root)
    compile_error_reasons = Counter()

    # os.environ["LANG"] = "en_US.UTF-8"
    # os.environ["LC_ALL"] = "en_US.UTF-8"

    if 'Codec' in root or 'JacksonDatabind' in root or 'Mockito' in root:
        os.environ['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8'
    else:
        os.environ['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=ISO-8859-1'
    env = os.environ.copy()

    compile_proc = subprocess.run(
        [d4j_command, "compile"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    del os.environ['JAVA_TOOL_OPTIONS']

    os.chdir(cur_dir)

    # extracting error message
    compile_error_lines = compile_proc.stderr.decode("utf-8").split("\n")[2:]
    compile_error_lines = [
        e
        for e in compile_error_lines
        if ("[javac] [" not in e) or ("[exec] [" not in e)
    ]
    compile_error_lines = [
        e for e in compile_error_lines if ("[javac]" in e) or ("[exec]" in e)
    ]
    compile_error_lines = [e for e in compile_error_lines if "warning:" not in e]
    compile_error_lines = [e for e in compile_error_lines if "[javac] Note:" not in e]
    compile_error_lines = [
        e for e in compile_error_lines if "compiler be upgraded." not in e
    ]
    compile_error_msg = "\n".join(compile_error_lines)

    for line in compile_error_lines:
        if "error:" in line:
            start = line.find("error:")
            if start != -1:
                compile_error_reasons[line[start:]] += 1
    compile_flag = True
    if compile_proc.returncode != 0:
        compile_flag = False
    return compile_flag, compile_error_msg, compile_error_reasons


def check_compile(bug_id):
    """
    检查在fixed以及buggy版本上能否编译成功

    Args:
        bug_id (str): 指定的目标bug id

    Raises:
        FileNotFoundError: 如果fixed或者buggy文件夹不存在，则抛出FileNotFoundError

    Returns:
        dict: {
            "fixed_pass":fixed版本上是否编译成功（1表示编译成功，0表示失败，下同），
            “fixed_error_info”:fixed版本上编译失败的terminal输出，
            "fixed_errors":fixed版本上编译失败的原因以及出现次数的计数，
            "buggy_pass":buggy版本上是否编译成功
        }
    """
    fixed_dir = os.path.join(d4j_proj_base, f"{bug_id}/fixed")
    buggy_dir = os.path.join(d4j_proj_base, f"{bug_id}/buggy")
    if os.path.exists(fixed_dir) and os.path.exists(buggy_dir):

        # 去掉一些影响编译的已有测试用例
        if bug_id.startswith("Lang"):
            for dir in [fixed_dir, buggy_dir]:
                if os.path.exists(f"{dir}/src/test/org/apache/commons/lang/enum"):
                    os.system(f"rm -rf {dir}/src/test/org/apache/commons/lang/enum")
                if os.path.exists(f"{dir}/src/test/org/apache/commons/lang/AllLangTestSuite.java"):
                    os.system(f"rm -f {dir}/src/test/org/apache/commons/lang/AllLangTestSuite.java")

        if bug_id.startswith('Codec'):
            for dir in [fixed_dir, buggy_dir]:
                if os.path.exists(f"{dir}/src/test/org/apache/commons/codec/language/ColognePhoneticTest.java"):
                    # org/apache/commons/codec/language/ColognePhoneticTest.java:113
                    os.system(f"rm -rf {dir}/src/test/org/apache/commons/codec/language/ColognePhoneticTest.java")
                # src/test/org/apache/commons/codec/binary/Base64Test.java
                if os.path.exists(f"{dir}/src/test/org/apache/commons/codec/binary/Base64Test.java"):
                    os.system(f"rm -rf {dir}/src/test/org/apache/commons/codec/binary/Base64Test.java")

        fixed_pass, fixed_err_info, fixed_errors = _compile_and_collect_results(
            fixed_dir
        )
        buggy_pass, _, _ = _compile_and_collect_results(buggy_dir)
        return {
            "fixed_pass": fixed_pass,
            "fixed_error_info": fixed_err_info,
            "fixed_errors": fixed_errors,
            "buggy_pass": buggy_pass,
        }
    else:
        raise FileNotFoundError()


def _summarize_test_failures(err_str):
    """
    根据测试的执行结果，分析终端输出

    Args:
        err_str (str): defects4j test 的终端输出内容

    Returns:
        test_error_types (list): 测试过程中出现的错误（Exception）
        test_error_info (list): 测试过程中出现的完整错误信息
    """
    lines = err_str.split("\n")
    raw_errs = []
    test_error_types = []
    test_error_info = []
    for index, line in enumerate(lines):
        line = line.strip()
        if line.startswith("---") and index + 1 in range(len(lines)):
            raw_errs.append(lines[index + 1])

    for raw_err in raw_errs:
        match = re.search(r"(.*[Error|Exception])[: (.*)]{0,1}", raw_err)
        if match:
            exception_type = match.group(1)
            test_error_types.append(exception_type)
            try:
                exception_info = match.group(2)
                test_error_info.append(exception_info)
            except Exception as e:
                exception_info = exception_type
                test_error_info.append(exception_info)
        else:
            print(f"Did not find any exception in {raw_err}")
            continue

    return test_error_types, test_error_info


def _test_and_collect_results(root, target_bz_file=None):
    """
    执行测试，并收集测试结果

    Args:
        root (str): 执行测试的根目录 (如Chart_1/fixed)

    Raises:
        FileNotFoundError: 测试的根目录不存在
        UncompilableWhileTestException: 测试类无法通过编译，应该通过编译的测试类才会进入测试阶段
        NotImplementedError: 在分析运行结果(Running ant (run.dev.tests)）时出现了未知的后缀类型
        TestResultNotFoundException: 测试结果没有收集到，有可能的错误：空的测试类

    Returns:
        dict : {
            "passed":是否通过测试，boolean类型,
            "error_types": 测试出错的类型list,
            "error_info": 测试出错的信息
        }
    """
    if not os.path.exists(root):
        raise FileNotFoundError()
    else:
        cur_dir = os.getcwd()
        os.chdir(root)
        if target_bz_file is not None:
            test_cmd = f"timeout 10 {d4j_command} test -s {target_bz_file}"
            pass
        else:
            test_cmd = f"timeout 10 {d4j_command} test"
        process = subprocess.Popen(
            test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = process.communicate(timeout=10)
            return_code = process.returncode
            if return_code == 124:
                return {
                    "passed": False,
                    "error_types": ["timeout"],
                    "error_info": ["timeout"],
                }
        except subprocess.TimeoutExpired as te:
            os.kill(process.pid, signal.SIGKILL)

            return {
                "passed": False,
                "error_types": ["timeout"],
                "error_info": ["timeout"],
            }
        test_flag = False
        test_error_info = []
        test_error_types = []
        if return_code == 0:
            # test命令正常结束了
            cmd_output = stdout.decode(encoding="utf-8").strip()
            cmd_err = stderr.decode(encoding="utf-8").strip()
            # try:
            #     assert cmd_err.endswith("OK")
            # except AssertionError:
            #     raise PassButFailException(
            #         f"{root} should pass, but not. Return code of the test command is {return_code}."
            #     )

            lines = cmd_output.split("\n")
            for line in lines:
                if line.startswith("Failing tests:"):
                    num_failed = re.findall(r"Failing tests: (\d+)", line)
                    assert len(num_failed) == 1
                    num_failed = int(num_failed[0])
                    if num_failed == 0:
                        # pass test
                        test_flag = True
                        test_error_types = ["pass"]
                        test_error_info = ["success"]
                        break
                    else:
                        assert len(lines) == num_failed + 1
                        test_flag = False
                        if os.path.exists(root + "/failing_tests"):
                            with open(
                                    os.path.join(root, "failing_tests"),
                                    "r",
                                    encoding="utf-8",
                            ) as reader:
                                content = reader.read()

                            # 根据执行失败的错误信息判断错误类型和数量
                            (
                                test_error_types,
                                test_error_info,
                            ) = _summarize_test_failures(content)
                        else:
                            test_error_types = ["unknown"]
                            test_error_info = ["unknown"]
                        break
                else:
                    raise NotImplementedError(f"ERROR: Cannot process: {line}.")
            pass
        else:
            # test 命令没有正常结束
            failing_test_str = stderr.decode("utf-8").strip()
            output_lines = failing_test_str.split("\n")
            for line in output_lines:
                # 测试类的编译过程结果检查
                if line.startswith("Running ant (compile.tests)"):
                    if line.endswith("OK"):
                        # do nothing, it should be ok
                        pass
                    else:
                        os.chdir(cur_dir)
                        raise UncompilableWhileTestException(
                            f"{root}: should be compilable, but not."
                        )
                    pass

                # 测试类的测试结果检查
                if line.startswith("Running ant (run.dev.tests)"):
                    if line.endswith("FAIL"):
                        test_flag = False
                        if os.path.exists(root + "/failing_tests"):
                            with open(
                                    os.path.join(root, "failing_tests"),
                                    "r",
                                    encoding="utf-8",
                            ) as reader:
                                content = reader.read()

                            # 根据执行失败的错误信息判断错误类型和数量
                            (
                                test_error_types,
                                test_error_info,
                            ) = _summarize_test_failures(content)
                            break
                        else:
                            test_error_types.append("unknown")
                            test_error_info.append("unknown")
                            break
                    elif line.endswith("OK"):
                        raise FailButTestOKException(
                            f"{root} should fail, but not. Return code of the test command is {return_code}."
                        )
                    else:
                        raise NotImplementedError(f"ERROR: Cannot process: {line}.")
                else:
                    # 暂时不处理其他的输出内容
                    continue
            if test_flag is None:
                raise TestResultNotFoundException(f"{root}: test results not found.")

    os.chdir(cur_dir)
    return {
        "passed": test_flag,
        "error_types": test_error_types,
        "error_info": test_error_info,
    }


def to_jave_bytecode_types(c_str: str):
    # ["B", "C", "D", "F", "I", "J", "Z", "S"]
    if c_str == "B":
        return "java.lang.byte"
    elif c_str == "C":
        return "java.lang.character"
    elif c_str == "D":
        return "java.lang.double"
    elif c_str == "F":
        return "java.lang.float"
    elif c_str == "I":
        return "java.lang.integer"
    elif c_str == "J":
        return "java.lang.long"
    elif c_str == "Z":
        return "java.lang.boolean"
    elif c_str == "S":
        return "java.lang.short"
    elif c_str.startswith("L"):
        return c_str[1:].replace("/", ".")
    elif c_str.startswith("["):
        return to_jave_bytecode_types(c_str[1:]) + "[]"
    else:
        raise NotImplementedError("class type %s not implemented yet" % c_str)


def encode_java_bytecode_types(param_list: list):
    res = ''
    for param in param_list:
        if param == 'java.lang.byte':
            res += 'B'
        elif param == 'java.lang.character':
            res += 'C'
        elif param == 'java.lang.double':
            res += 'D'
        elif param == 'java.lang.float':
            res += 'F'
        elif param == 'java.lang.integer':
            res += 'I'
        elif param == 'java.lang.long':
            res += 'J'
        elif param == 'java.lang.boolean':
            res += 'Z'
        elif param == 'java.lang.short':
            res += 'S'
        elif param.endswith('[]'):
            res += '[' + encode_java_bytecode_types([param[:-2]])
        else:
            raise NotImplementedError(f"class type {param} not implemented yet.")

    pass


def parse_coverage_xml(coverage_report):
    """
    Load and parse the JaCoCo XML coverage report

    Args:
        coverage_report (str): jacoco生成的覆盖率报告路径

    Raises:
        NotImplementedError: 不支持的变量类型，请联系开发人员

    Returns:
        dict: 经过分析之后的jacoco覆盖率指标
    """
    tree = ET.parse(coverage_report)
    root = tree.getroot()

    coverage_data = defaultdict()
    # Iterate over the packages in the XML and collect data
    for package in root.findall(".//package"):
        package_name = package.attrib["name"]
        coverage_data[package_name] = defaultdict()

        for clazz in package.findall(".//class"):
            clazz_name = clazz.attrib["name"]
            if clazz.findall(".//method"):
                coverage_data[package_name][clazz_name] = defaultdict()

                for method in clazz.findall(".//method"):
                    method_name = method.attrib["name"]
                    pattern = r"\(.*?\)"
                    parameters = re.findall(pattern, method.attrib["desc"])[0][1:-1]
                    raw_param_list = parameters.split(";")
                    parameter_list = []

                    for param_str in raw_param_list:
                        if param_str == "":
                            continue
                        else:
                            param_stack = []

                            for i in range(len(param_str)):
                                c_str = param_str[i]
                                if c_str == "[":
                                    param_stack.append(c_str)
                                    continue
                                elif c_str == "L":
                                    param_stack.append(param_str[i:])
                                    res = "".join(param_stack)
                                    parameter_list.append(
                                        to_jave_bytecode_types(res).lower()
                                    )
                                    param_stack.clear()
                                    break
                                elif c_str in ["B", "C", "D", "F", "I", "J", "Z", "S"]:
                                    param_stack.append(c_str)
                                    pass
                                else:
                                    raise NotImplementedError(
                                        "Class Type %s not implemented yet." % c_str
                                    )
                                res = "".join(param_stack)
                                parameter_list.append(
                                    to_jave_bytecode_types(res).lower()
                                )
                                param_stack.clear()

                    tmp_list = []
                    for i in parameter_list:
                        if "/" in i:
                            tmp_list.append(i.split("/")[-1])
                        else:
                            tmp_list.append(i)
                    parameter_tuple = tuple(tmp_list)

                    if method_name not in coverage_data[package_name][clazz_name]:
                        coverage_data[package_name][clazz_name][
                            method_name
                        ] = defaultdict()
                    coverage_data[package_name][clazz_name][method_name][
                        parameter_tuple
                    ] = defaultdict()
                    if method.find('.//counter[@type="LINE"]') is not None:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["line_coverage"] = method.find(
                            './/counter[@type="LINE"]'
                        ).attrib
                    else:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["line_coverage"] = None
                    if method.find('.//counter[@type="BRANCH"]') is not None:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["branch_coverage"] = method.find(
                            './/counter[@type="BRANCH"]'
                        ).attrib
                    else:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["branch_coverage"] = None
    return coverage_data


def evosuite_test(bug_id, report_dir):
    fixed_passed = False
    fixed_coverage = {}
    buggy_passed = False
    fixed_err_types = []
    fixed_err_info = []
    fixed_dir = os.path.join(d4j_proj_base, f"{bug_id}/fixed")
    buggy_dir = os.path.join(d4j_proj_base, f"{bug_id}/buggy")
    if os.path.exists(fixed_dir) and os.path.exists(buggy_dir):
        if os.path.exists(report_dir):
            os.system(f"rm -rf {report_dir}")
        os.makedirs(report_dir, exist_ok=True)
        environ = f"-javaagent:{code_base}/utils/jacoco/lib/jacocoagent.jar=destfile={report_dir}/report.exec"
        os.environ["JAVA_TOOL_OPTIONS"] = environ
        bz_file_path = _compress_evosuite_bz_files(bug_id, "fixed")
        fixed_res = _test_and_collect_results(fixed_dir, target_bz_file=bz_file_path)
        # os.system(f"rm {bz_file_path}")
        fixed_passed = fixed_res["passed"]
        fixed_err_info = fixed_res["error_info"]
        fixed_err_types = fixed_res["error_types"]
        fixed_coverage = _check_coverage(fixed_dir, bug_id, report_dir)
        del os.environ["JAVA_TOOL_OPTIONS"]
        # bz_file_path = _compress_evosuite_bz_files(bug_id, "buggy")
        buggy_res = _test_and_collect_results(buggy_dir, target_bz_file=bz_file_path)
        os.system(f"rm {bz_file_path}")
        buggy_passed = buggy_res["passed"]
        pass
    else:
        raise FileNotFoundError()
    return {
        "fixed_passed": fixed_passed,
        "buggy_passed": buggy_passed,
        "fixed_coverage": fixed_coverage,
        "fixed_error_types": fixed_err_types,
        "fixed_error_info": fixed_err_info,
    }
    pass


def _compress_evosuite_bz_files(bug_id, version):
    if version == "fixed":
        test_base = os.path.join(d4j_proj_base, bug_id, "fixed", "evosuite-tests")
    elif version == "buggy":
        test_base = os.path.join(d4j_proj_base, bug_id, "fixed", "evosuite-tests")
    else:
        raise NotImplementedError(f"Unknown version {version}")

    cur_root = os.getcwd()
    os.chdir(test_base)
    # test_file = test_class_file.replace('.', '/') + '.java'
    # if not os.path.exists(test_file):
    #     raise FileNotFoundError(f"Target test file {test_file} not found.")
    os.system(f"tar -vcjf LLMGeneratedTests.tar.bz ./ 2>/dev/null")
    os.chdir(cur_root)
    return os.path.join(str(test_base), "LLMGeneratedTests.tar.bz")

def _check_coverage(directory_path, bug_id, report_dir):
    """
    执行完测试之后，收集coverage数据

    Args:
        directory_path (str): 目标项目的路径
        bug_id (str): 具体的defects4j bug
        report_dir (str): jacoco生成的报告路径

    Returns:
        dict: 经过分析后的jacoco覆盖率指标
    """
    # 加载对应项目的src和test的路径
    with open(f"{code_base}/data/test_src.json", "r") as f:
        content_path = json.load(f)

    project_name = bug_id
    if content_path[project_name.lower()]["src_class"][0] != "/":
        class_base = content_path[project_name.lower()]["src_class"]
    else:
        class_base = content_path[project_name.lower()]["src_class"][1:]
    class_base_dir = os.path.join(directory_path, class_base)

    if content_path[project_name.lower()]["src"][0] != "/":
        src_base = content_path[project_name.lower()]["src"]
    else:
        src_base = content_path[project_name.lower()]["src"][1:]
    src_base_dir = os.path.join(directory_path, src_base)

    cur_dir = os.getcwd()
    os.chdir(directory_path)

    row_report = f"{report_dir}/report.exec"
    report_file = f"{report_dir}/report.xml"

    commands = [
        "java",
        "-jar",
        f"{code_base}/utils/jacoco/lib/jacococli.jar",
        "report",
        f"{row_report}",
        f"--classfiles {class_base_dir}",
        f"--sourcefiles {src_base_dir}",
        f"--xml {report_file}",
    ]
    cmd = " ".join(commands)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise JacocoFailedException(
            f"Failed in analyzing the coverage results for {bug_id}."
        )
    os.chdir(cur_dir)
    coverage_data = parse_coverage_xml(report_file)
    return coverage_data


def check_test(bug_id, test_class_sig, report_dir):
    fixed_passed = False
    fixed_coverage = {}
    buggy_passed = False
    fixed_err_types = []
    fixed_err_info = []
    fixed_dir = os.path.join(d4j_proj_base, f"{bug_id}/fixed")
    buggy_dir = os.path.join(d4j_proj_base, f"{bug_id}/buggy")
    if os.path.exists(fixed_dir) and os.path.exists(buggy_dir):
        if os.path.exists(report_dir):
            os.system(f"rm -rf {report_dir}")
        os.makedirs(report_dir, exist_ok=True)
        environ = f"-javaagent:{code_base}/utils/jacoco/lib/jacocoagent.jar=destfile={report_dir}/report.exec"
        os.environ["JAVA_TOOL_OPTIONS"] = environ
        bz_file_path = _compress_bz_files(bug_id, "fixed", test_class_sig)
        fixed_res = _test_and_collect_results(fixed_dir, target_bz_file=bz_file_path)
        os.system(f"rm {bz_file_path}")
        fixed_passed = fixed_res["passed"]
        fixed_err_info = fixed_res["error_info"]
        fixed_err_types = fixed_res["error_types"]
        fixed_coverage = _check_coverage(fixed_dir, bug_id, report_dir)
        del os.environ["JAVA_TOOL_OPTIONS"]
        bz_file_path = _compress_bz_files(bug_id, "buggy", test_class_sig)
        buggy_res = _test_and_collect_results(buggy_dir, target_bz_file=bz_file_path)
        os.system(f"rm {bz_file_path}")
        buggy_passed = buggy_res["passed"]
        pass
    else:
        raise FileNotFoundError()
    return {
        "fixed_passed": fixed_passed,
        "buggy_passed": buggy_passed,
        "fixed_coverage": fixed_coverage,
        "fixed_error_types": fixed_err_types,
        "fixed_error_info": fixed_err_info,
    }
    pass


def _compress_bz_files(bug_id, version, test_class_sig):
    fixed_test_base, buggy_test_base = _get_test_location_by_bug_id(bug_id)
    if version == "fixed":
        test_base = fixed_test_base
    elif version == "buggy":
        test_base = buggy_test_base
    else:
        raise NotImplementedError(f"Unknown version {version}")
    cur_root = os.getcwd()
    os.chdir(test_base)
    test_file = test_class_sig.replace('.', '/') + '.java'
    if not os.path.exists(test_file):
        raise FileNotFoundError(f"Target test file {test_file} not found.")
    os.system(f"tar -vcjf LLMGeneratedTests.tar.bz {test_file} 2>/dev/null")
    os.chdir(cur_root)
    return os.path.join(str(test_base), "LLMGeneratedTests.tar.bz")


if __name__ == "__main__":
    summarize_d4j_test_shell()
