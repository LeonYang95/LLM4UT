from utils.d4j_utils import *
from utils.java_parser import (
    parse_import_nodes_from_file_code,
)
from utils.output_analyzer import assemble_recursive_test_classes, assemble_empty_test_file


def compile_and_test(
    bug_id,
    test_class_sig,
    test_class_content,
    focal_method_name,
    compile_level,
    round,
    model,
    strategy,
    ablation,
    format,
):
    if test_class_sig is None:
        raise NoneTestClassDefinedException("ERROR: There is no test class defined.")
        pass


    # 获得编译结果
    compile_res = check_compile(bug_id)

    jacoco_report_base = os.path.join(
        code_base,
        f"rq1/coverage_reports/{compile_level}/{model}_{strategy}_{ablation}_{format}/{round}/{bug_id}_{focal_method_name}",
    )
    if compile_res["fixed_pass"]:
        # 获得测试结果
        execute_res = check_test(bug_id, test_class_sig,jacoco_report_base)
        pass
    else:
        execute_res = None

    return _analyze_compile_res(compile_res, execute_res, test_class_content, round)


def _analyze_compile_res(compile_res, execute_res, test_class_content, round):
    methods = parse_methods_from_class_node(test_class_content, False)
    uts = [method for method in methods if "@Test" in method["method_modifiers"]]
    total_methods_num = len(methods)
    total_uts_num = len(uts)
    new_content = pickle.loads(pickle.dumps(test_class_content))
    imports = parse_import_nodes_from_file_code(test_class_content)
    fields = parse_fields_from_class_code(test_class_content, False)
    if compile_res["fixed_pass"]:
        coverage_results = execute_res
        compiled = True
        compiled_uts_num = len(uts)
        compiled_methods_num = len(methods)
        passed_methods = methods
        passed_uts = uts
        passed_imports = [imp["text"] for imp in imports]
        failed_imports = {}
        failed_methods = {}
        err_types = []
        msg = "success"
    else:
        coverage_results = execute_res
        compiled = False
        msg = "failed"
        compiled_uts_num = len(uts)
        compiled_methods_num = len(methods)
        # 筛选出编译错误中出现错误的行号
        error_line_idxes, err_types = get_sorted_error_line_num(
            error_str=compile_res["fixed_error_info"]
        )

        # 根据行号判断是否有import中的编译错误
        failed_imports, passed_imports, missing_err_lines = find_failed_imports(
            target_lines=error_line_idxes, imports=imports
        )

        if len(failed_imports) != 0:
            # 如果有import出错，那么需要去掉import之后重新编写测试类然后重新compile
            msg = "recompile"
            ret_dict = {
                "compiled": compiled,
                "err_msg": compile_res["fixed_error_info"],
                "err_types": err_types,
                "msg": msg,
                "total_methods_num": total_methods_num,
                "total_uts_num": total_uts_num,
                "passed_uts_num": len(uts),
                "passed_methods_num": len(methods),
                "passed_uts": uts,
                "passed_methods": methods,
                "passed_imports": passed_imports,
                "failed_imports": failed_imports,
                "fields": fields,
                "new_content": new_content,
                "coverage_results": coverage_results,
                "failed_methods": methods,
            }
            return ret_dict
        else:
            # 如果没有import出错，筛选出现编译错误的函数，重新组合测试类，进行第二次编译
            if len(missing_err_lines) != len(error_line_idxes):
                raise IndexError(
                    f"missing error lines should be the same as original after import stmt filter, but have {len(missing_err_lines)} and {len(error_line_idxes)}"
                )

            # 根据行号找到对应的method（如有）
            failed_methods, passed_methods, missing_err_lines = find_failed_methods(
                target_lines=error_line_idxes, methods=methods
            )

            passed_uts = [
                method
                for method in passed_methods
                if "@Test" in method["method_modifiers"]
            ]
            compiled_uts_num = len(passed_uts)

            # 根据编译出错的函数信息，更新一下函数级编译率计数器。如果出现应当计数为0的情况，那么passed_methods为空
            if len(failed_methods) != 0:
                compiled_methods_num = update_compilable_method_count(
                    failed_methods, compiled_methods_num
                )
                # 如果经过判断，没有任何一个函数通过编译，那么这里就不应该有ut通过编译
                if compiled_methods_num == 0:
                    compiled_uts_num = 0
                    passed_uts.clear()
                try:
                    assert compiled_uts_num <= compiled_methods_num
                except AssertionError as ae:
                    print(
                        f"Compilable uts should be less than compilable methods, but found {compiled_uts_num} > {compiled_methods_num}"
                    )
                    raise Exception("Unexpected number of passed uts")
                pass
            else:
                # 函数中没有出现编译错误，继续后面的步骤
                pass

            if compiled_methods_num == 0 or len(missing_err_lines) != 0:
                # 如果通过编译的函数计数为0，或者还有未解决的编译错误信息，那么认为编译失败，不进入第二轮编译
                passed_methods.clear()
                new_content = (
                    "public class TmpTest{\n"
                    "    @Test\n"
                    "    public void emptyTest(){\n"
                    "        assertTrue(true);\n"
                    "    }\n"
                    "}\n"
                )
                missing_err_lines.clear()
                compiled_uts_num = 0
                passed_uts.clear()
            else:
                # 如果已经把所有的编译错误都找到了，并且还有可以编译的函数，那么继续后面的步骤
                pass

    return {
        "compiled": compiled,
        "total_methods_num": total_methods_num,
        "total_uts_num": total_uts_num,
        "passed_methods_num": compiled_methods_num,
        "passed_uts_num": compiled_uts_num,
        "err_msg": compile_res["fixed_error_info"],
        "err_types": err_types,
        "msg": msg,
        "new_content": new_content,
        "coverage_results": coverage_results,
        "failed_methods": failed_methods,
        "passed_methods": passed_methods,
        "passed_uts": passed_uts,
        "failed_imports": failed_imports,
        "passed_imports": passed_imports,
        "fields": fields,
    }


def find_failed_methods(target_lines, methods):
    """
    返回包含目标便宜错误行的函数列表。

    :param target_lines: 一个包含目标编译错误信息的列表。
    :param methods: parse_methods_from_class_node的输出函数列表。
    :return: 一个method的列表，这些函数包含了至少一个目标行号，还有没有匹配到的行号
    """
    methods_contain_err = []
    methods_passed = []
    found_lines = set()

    for method in methods:
        start_line = method["method_start_line"]
        end_line = method["method_end_line"]
        if any(line in range(start_line, end_line + 1) for line in target_lines):
            function_range = set(range(start_line, end_line + 1))
            methods_contain_err.append(pickle.loads(pickle.dumps(method)))
            found_lines.update(function_range.intersection(target_lines))
        else:
            methods_passed.append(pickle.loads(pickle.dumps(method)))

    missing_lines = set(target_lines) - found_lines
    return methods_contain_err, methods_passed, missing_lines


def find_failed_imports(target_lines, imports):
    """
    返回包含目标便宜错误行的import语句。

    :param target_lines: 一个包含目标编译错误信息的列表。
    :param imports: parse_import_nodes_from_class_text的输出import dict列表。
    :return: 一个包含编译错误的import列表，一个通过编译的import列表，一个仍然没有匹配上的错误行号
    """
    imports_contain_err = []
    imports_passed = []
    found_lines = set()

    for import_node in imports:
        start_line = import_node["start"]
        end_line = import_node["end"]
        if any(line in range(start_line, end_line + 1) for line in target_lines):
            import_range = set(range(start_line, end_line + 1))
            imports_contain_err.append(pickle.loads(pickle.dumps(import_node["text"])))
            found_lines.update(import_range.intersection(target_lines))
        else:
            imports_passed.append(pickle.loads(pickle.dumps(import_node["text"])))

    missing_lines = set(target_lines) - found_lines
    return imports_contain_err, imports_passed, missing_lines


def update_compilable_method_count(failed_methods, maximum_count):
    """
    根据出错函数的信息，更新一下函数级别通过编译的函数数量

    Args:
        failed_methods (list): 包含编译错误的函数列表
        maximum_count (int): 整个测试类中包含的所有测试函数的数量，在此基础上减去出错函数的数量。

    Returns:
        int: 更新后的通过编译的函数数量
    """
    updated_count = pickle.loads(pickle.dumps(maximum_count))
    for method in failed_methods:
        if method["method_modifiers"] != "":
            # 提取标识符
            modifiers = [
                x.strip() for x in method["method_modifiers"].split() if x != ""
            ]
            if any(
                modifier.startswith("@")
                and modifier in ["@Before", "@BeforeClass", "@After", "@AfterClass"]
                for modifier in modifiers
            ):
                # 如果这个函数是setup函数，那么所有函数都不可编译，结束计数，同时清零passed_methods
                updated_count = 0
                break
            else:
                # 不是setup函数，那么就看看是不是test函数
                if any(modifier == "@Test" for modifier in modifiers):
                    updated_count -= 1
                else:
                    # 既不是setup，也不是test，应该是一些辅助函数
                    # TODO: 这里需要考虑一下，如果是辅助函数，是否认为所有函数都不可编译，结束计数，同时清零passed_methods
                    updated_count = 0
                    break

        else:
            # 没有modifier的函数，有且只有一种情况，构造函数，而且是私有的构造函数
            updated_count = 0
            break
    return updated_count


def get_sorted_error_line_num(error_str):
    """
    find code lines that contains compilation errors.

    Args:
        pattern (str): regex pattern to find eror
        error_str (str): compilation failure error output

    Returns:
        list: line INDEXES that contains compilation error, please note that INDEX means starts with 0.
    """
    pattern = r"\[.*\] .+\/defects4j\/d4j\_projects\/.*\.java:(\d+): error: (.*)"
    error_line_list = []
    error_list = error_str.split("\n")
    error_type_list = []
    for i in error_list:
        match_flag = re.match(pattern, i.strip())
        if match_flag:
            error_line_num = match_flag.group(1)
            error_line_list.append(error_line_num)
            error_type_list.append(match_flag.group(2))
    return [int(i) - 1 for i in sorted(list(set(error_line_list)))], error_type_list


def assemble_and_place_recompile_test_class(
    bug_id: str,
    package_name: str,
    class_name: str,
    imports: list,
    methods: list,
    fields: list,
    classes: list,
):
    """
    组装一个新的重新编译的测试类，和之前第一次组装的区别在于import是一次性给全的，而不是由不同部分组装而成的。

    Args:
        bug_id (str): d4j bug id
        package_name (str): 待测类的package info
        class_name (str): 待测类的类名
        imports (list): import list
        methods (list): UTs
        fields (list): 待测类中定义的属性
        classes (list): 待测类中定义的类

    Returns:
        str: 组装好的测试类的内容
    """
    test_content = assemble_recursive_test_classes(
        d4j_proj_base,
        bug_id,
        "fixed",
        class_name,
        package_name,
        imports,
        methods,
        fields,
        classes,
    )
    _ = assemble_recursive_test_classes(
        d4j_proj_base,
        bug_id,
        "buggy",
        class_name,
        package_name,
        imports,
        methods,
        fields,
        classes,
    )
    return test_content


def assemble_and_place_empty_test_classes(
    bug_id: str,
):
    test_content, class_name = assemble_empty_test_file()
    location = os.path.join(
        d4j_proj_base, "target", "test-classes", class_name + ".class"
    )
    return test_content, class_name, location


if __name__ == "__main__":
    pass
