from utils.cal_rate import *
from utils.dependency_analyzer import add_dependencies
from utils.java_parser import has_branch
from utils.output_analyzer import *

import_json_path = os.path.join(code_base, "data/import_v2.json")
with open(import_json_path, "r") as file:
    import_json = json.load(file)


def remove_content_in_parentheses(text):
    """
    去除括号内的内容

    Args:
        text (_type_): 原始的字符串

    Returns:
        str: 去除括号之后的内容
    """
    # This regex pattern finds a pair of parentheses and anything in between.
    pattern = r"\(.*?\)"

    # The re.sub function replaces the pattern with an empty string.
    new_text = re.sub(pattern, "", text)

    return new_text


def calculate_coverage_stats(
        focal_method,
        fixed_coverage_data,
        method_name,
        package_dir,
        clazz_dir,
        parameter_tuple,
):
    res_dict = {
        "msg": "success",
        "line_coverage_covered": -1,
        "line_coverage_missed": -1,
        "branch_coverage_covered": -1,
        "branch_coverage_missed": -1,
    }

    if method_name in fixed_coverage_data.get(package_dir, {}).get(clazz_dir, {}):
        focal_method_cov = fixed_coverage_data[package_dir][clazz_dir][method_name].get(
            parameter_tuple, None
        )

        if focal_method_cov is None:
            raise ParameterNotFoundException(
                f"Parameter tuple {parameter_tuple} not found."
            )

        if focal_method_cov["line_coverage"] is not None:
            res_dict["line_coverage_covered"] = int(
                focal_method_cov["line_coverage"]["covered"]
            )
            res_dict["line_coverage_missed"] = int(
                focal_method_cov["line_coverage"]["missed"]
            )
        if focal_method_cov["branch_coverage"] is not None and has_branch(focal_method):
            res_dict["branch_coverage_covered"] = int(
                focal_method_cov["branch_coverage"]["covered"]
            )
            res_dict["branch_coverage_missed"] = int(
                focal_method_cov["branch_coverage"]["missed"]
            )

    else:
        raise MethodNotFoundInJacocoException(
            f"method {method_name} not found in {package_dir}/{clazz_dir}"
        )

    return res_dict


def filter_data_according_to_project(input_file, assistant_data, target_project):
    """
    读取指定的输入文件，并且根据给定的project结合辅助数据筛选输入数据
    Args:
        input_file: 输入文件
        assistant_data: 辅助数据，帮助判断输入数据属于哪个项目
        target_project: 目标项目

    Returns:
        list: 过滤后的输入数据
    """
    # 使用辅助数据过滤目标project的数据
    res = []
    with open(input_file, "r", encoding="utf-8") as reader:
        lines = reader.readlines()
        for idx, line in tqdm(
                enumerate(lines),
                total=len(lines),
                desc="Reading generation file",
        ):
            line = line.strip()
            data = json.loads(line)
            if (
                    assistant_data[idx]["project"] == target_project
                    and assistant_data[idx]["is_public"] == "1"
            ):
                data["project"] = pickle.loads(
                    pickle.dumps(assistant_data[idx]["project"])
                )
                data["focal_method"] = pickle.loads(
                    pickle.dumps(assistant_data[idx]["focal_method"])
                )
                data['test_shell'] = pickle.loads(pickle.dumps(assistant_data[idx]['test_shell']))
                data["id"] = "_".join(assistant_data[idx]["id"].split("_")[:2])
                res.append(pickle.loads(pickle.dumps(data)))
    return res


def extract_elements_from_llm_generation(
        generation: str, strategy: str, method_signature: str
):
    """
    从LLM的输出结果中分析代码元素，组成测试类
    Args:
        generation: LLM的输出内容
        strategy: 生成策略，默认是extend
        method_signature: 待测函数签名

    Returns:
        dict:{
                "msg": 提取结果，"success", "no llm output" 或 "no methods in output"
                "methods":[method],
                "imports":[import],
                "fields":[field],
                "classes":[class],
                "uts": [ut],
             }
    """
    # 当LLM有正确输出的时候才进行下一步
    msg = "no llm output"
    imports, fields, classes, methods, uts = [], [], [], [], []
    if generation != "":
        methods, imports, fields, classes = analyze_outputs(
            generation,
            strategy,
            method_signature=method_signature,
        )
        uts = [method for method in methods if method.strip().startswith("@Test")]
        msg = "success"

    # 如果没有提取到任何method
    if len(methods) == 0:
        methods, imports, fields, classes = [], [], [], []
        msg = "no methods in output"
        uts = []

    return {
        "msg": msg,
        "methods": methods,
        "imports": imports,
        "fields": fields,
        "classes": classes,
        "uts": uts,
    }


def extract_elements_from_test_shell(test_shell: str):
    msg = "no llm output"
    imports, fields, classes, methods, uts = [], [], [], [], []
    if test_shell != "":
        methods = [method['method_text'] for method in parse_methods_from_class_node(test_shell, need_prefix=False)]
        imports = parse_import_stmts_from_file_code(test_shell)
        fields = [field["declaration_text"] for field in parse_fields_from_class_code(test_shell)]
        uts = [method for method in methods if method.strip().startswith("@Test")]
        msg = "success"

    # 如果没有提取到任何method
    if len(methods) == 0:
        methods, imports, fields, classes = [], [], [], []
        msg = "no methods in output"
        uts = []

    return {
        "msg": msg,
        "methods": methods,
        "imports": imports,
        "fields": fields,
        "classes": classes,
        "uts": uts,
    }


def analyze_method_signature_for_coverage(method_signature):
    """
    根据待测函数签名，分析收集覆盖率时需要的一些信息，例如类名，包名，函数名，以及变量列表
    Args:
        method_signature: 函数签名

    Returns:
        package_name: 包名
        package_dir: 包名对应的jacoco路径
        class_name: 类名
        class_dir: 类名对应的jacoco路径
        method_name: 函数名
        parameter_tuple: 参数列表
    """
    parameters = re.findall(r"\(.*?\)", method_signature)[0][1:-1]
    parameter_list = [i for i in parameters.split(",") if i != ""]
    tmp_list = []
    for i in parameter_list:
        if "#" in i:
            i = i.replace("#", ".")
        tmp_list.append(i.strip().lower())

    parameter_tuple = tuple(tmp_list)
    package_name = method_signature.split("#")[0]
    class_name = ".".join(method_signature.split("#")[:2])

    ## 测试覆盖率需要的条件
    package_dir = package_name.replace(".", "/")
    clazz_dir = class_name.replace(".", "/")
    method_name = remove_content_in_parentheses(
        "".join(method_signature.split("#")[2:])
    )
    return (
        package_name,
        package_dir,
        class_name,
        clazz_dir,
        method_name,
        parameter_tuple,
    )


def _inner_run(bug_id, package_name, class_name, method_name, extractions, model, strategy, ablation, format):
    """
    迭代编译，直到编译成功为止，收集编译结果
    Args:
        bug_id: bug id
        package_name: 待测类的包名
        class_name: 待测类的类名
        method_name: 待测函数的函数名
        extractions: 从llm generation中提取的信息
        model: 目标模型
        strategy: llm生成策略
        ablation: 消融实验变体
        format: llm prompt的格式

    Returns:
        {
            "first_compile_res": 第一轮编译结果，
            ”first_test_class“: 第一轮测试类，
            ”second_test_class": 第二轮测试类，
            “second_compile_res": 第二轮编译结果，
            ”is_empty_test“： 是否最后是一个空的测试类，
            ”retry_times": 直到成功编译，迭代了多少次,
            "num_uts": 一共有多少ut，
            "num_compilable_uts": 有多少ut成功通过编译，
            “num_passed_uts": 有多少ut成功运行
            ”num_executed_uts“: 有多少ut运行了（无论成功还是失败）
        }
    """
    res_dict = {}
    empty_test = False
    res_dict["num_uts"] = len(
        [m for m in extractions["methods"] if m.startswith("@Test")]
    )

    place_empty = False
    first_round_test_content = ""
    first_round_test_sig = None
    if extractions["msg"] == "success":
        # 收集到了足够的信息
        try:
            (
                first_round_test_content,
                first_round_test_sig,
            ) = assemble_first_round_test_class(
                bug_id,
                class_name,
                extractions["imports"],
                extractions["methods"],
                extractions["fields"],
                import_json,
                extractions["classes"],
            )
            for version in ["buggy", "fixed"]:
                write_test_file(
                    bug_id=bug_id,
                    version=version,
                    class_sig=first_round_test_sig,
                    content=first_round_test_content,
                )
        except UnicodeDecodeError as e:
            for version in ["buggy", "fixed"]:
                delete_test_file(bug_id, version, class_sig=first_round_test_sig)
            place_empty = True

    else:
        place_empty = True

    if place_empty:
        # 如果没有提取llm输出失败，或者遇到了编码问题，则给一个空的测试类进行测试
        first_round_test_content, first_round_test_sig = assemble_empty_test_file()
        for version in ["buggy", "fixed"]:
            write_test_file(
                bug_id=bug_id,
                version=version,
                class_sig=first_round_test_sig,
                content=first_round_test_content,
            )
        empty_test = True
        pass

    # 记录首轮整合完毕之后的文件内容
    res_dict["first_test_class"] = first_round_test_content

    ## 测试编译率
    add_dependencies(d4j_proj_base, bug_id)

    first_round_res = compile_and_test(
        bug_id,
        first_round_test_sig,
        first_round_test_content,
        method_name,
        "class_cov_dir",
        "first",
        model,
        strategy,
        ablation,
        format,
    )
    res_dict["first_compile_res"] = first_round_res
    res_dict["first_test_class"] = first_round_test_content

    for version in ['buggy', 'fixed']:
        delete_test_file(bug_id, version, first_round_test_sig)

    compile_errors = Counter()
    retry_times = 0
    if first_round_res["compiled"]:
        # 第一轮就通过编译了，不需要进行第二轮
        second_round_res = pickle.loads(pickle.dumps(first_round_res))
        second_round_test_class_sig = first_round_test_sig
        second_round_test_content = pickle.loads(pickle.dumps(first_round_test_content))
        pass
    else:
        # 定义初始循环
        second_round_res = pickle.loads(pickle.dumps(first_round_res))
        second_round_test_class_sig = first_round_test_sig
        # 循环终止条件：通过编译，或者直到所有的UT都被过滤为止
        while True:
            compile_errors.update(second_round_res["err_types"])
            retry_times += 1
            new_imports = second_round_res["passed_imports"]
            new_methods = [
                method["method_text"] for method in second_round_res["passed_methods"]
            ]
            for version in ["buggy", "fixed"]:
                delete_test_file(bug_id, version, class_sig=second_round_test_class_sig)

            if second_round_res["passed_uts_num"] == 0:
                # 如果没有passed ut，那么说明只需要收集一下覆盖率即可，给出一个空且可执行的测试类
                second_round_test_content, second_round_test_class_sig = assemble_empty_test_file()
                for version in ["buggy", "fixed"]:
                    write_test_file(
                        bug_id=bug_id,
                        version=version,
                        class_sig=second_round_test_class_sig,
                        content=second_round_test_content,
                    )
                empty_test = True
                pass
            else:

                # 如果有，那么就继续编译
                new_fields = extractions["fields"]
                new_classes = extractions["classes"]

                second_round_test_content, second_round_test_class_sig = assemble_recursive_test_classes(
                    package_name=package_name,
                    imports=new_imports,
                    methods=new_methods,
                    fields=new_fields,
                    classes=new_classes,
                )
                for version in ['buggy', 'fixed']:
                    write_test_file(
                        bug_id=bug_id,
                        version=version,
                        class_sig=second_round_test_class_sig,
                        content=second_round_test_content,
                    )

            second_round_res = compile_and_test(
                bug_id,
                second_round_test_class_sig,
                second_round_test_content,
                method_name,
                "function_cov_dir",
                "second",
                model,
                strategy,
                ablation,
                format,
            )

            if second_round_res["compiled"] or empty_test:
                for version in ['buggy', 'fixed']:
                    delete_test_file(bug_id, version, second_round_test_class_sig)
                break

    res_dict["is_empty_test"] = empty_test
    res_dict["second_compile_res"] = second_round_res
    res_dict["second_test_class"] = second_round_test_content
    res_dict["retry_times"] = retry_times
    res_dict["num_compilable_uts"] = (
        second_round_res["passed_uts_num"] if not empty_test else 0
    )
    fail_but_executable = []
    totally_failed = []
    if second_round_res["coverage_results"] is not None:
        for err_info in second_round_res["coverage_results"]["fixed_error_info"]:
            if err_info.startswith(
                    "junit.framework.AssertionFailedError"
            ) or err_info.startswith("java.lang.Exception: Unexpected exception"):
                fail_but_executable.append(1)
            else:
                totally_failed.append(1)
    else:
        for version in ['buggy', 'fixed']:
            delete_test_file(bug_id, version, second_round_test_class_sig)
        raise EmptyTestClassFailedCompileException(
            f"ERROR: {bug_id} failed compilation even though was given an empty test class.")

    res_dict["num_executed_uts"] = (
        (second_round_res["passed_uts_num"] - len(totally_failed))
        if not empty_test
        else 0
    )
    res_dict["num_passed_uts"] = (
        (
                second_round_res["passed_uts_num"]
                - len(totally_failed)
                - len(fail_but_executable)
        )
        if not empty_test
        else 0
    )
    return res_dict


def run(model, strategy, ablation, format, data, index):
    extraction_from_llm_outputs = Counter()
    res_dict = pickle.loads(pickle.dumps(data))
    # 拆分代码
    llm_output = data["completion"]
    res_dict["output"] = llm_output
    res_dict["index"] = index
    bug_id = data["id"]  # Chart_10
    res_dict["bug_id"] = bug_id
    focal_method = data["focal_method"]
    method_signature = data["method_signature"]

    extractions = extract_elements_from_llm_generation(
        llm_output, strategy, method_signature
    )

    # 更新测试用例壳的信息
    shell_extractions = extract_elements_from_test_shell(data['test_shell'])
    for key, item in extractions.items():
        if key != "msg":
            extractions[key] = pickle.loads(pickle.dumps(list(item) + shell_extractions[key]))

    extraction_from_llm_outputs[extractions["msg"]] += 1

    (
        package_name,
        package_dir,
        class_name,
        clazz_dir,
        method_name,
        parameter_tuple,
    ) = analyze_method_signature_for_coverage(method_signature)

    try:
        compile_res = _inner_run(
            bug_id=bug_id,
            method_name=method_name,
            class_name=class_name,
            package_name=package_name,
            extractions=extractions,
            model=model,
            strategy=strategy,
            ablation=ablation,
            format=format,
        )
        # 记录重试了多少次
        res_dict["retry_times"] = compile_res["retry_times"]
        res_dict["is_empty_test"] = compile_res["is_empty_test"]
        # 记录函数级别的编译率, 通过编译的个数等于第二轮成功编译的情况下的通过个数，总个数则是第一轮编译的时候所有的UT的个数
        res_dict["first_compile_res"] = compile_res["first_compile_res"]["msg"]
        res_dict["second_compile_res"] = compile_res["second_compile_res"]["msg"]

        res_dict["first_compile_error"] = compile_res["first_compile_res"]["err_msg"]
        res_dict["second_compile_error"] = compile_res["second_compile_res"]["err_msg"]
        total_uts = compile_res["num_uts"]
        num_compilable_uts = compile_res["num_compilable_uts"]
        num_executed_uts = compile_res["num_executed_uts"]
        num_passed_uts = compile_res["num_passed_uts"]

        res_dict["num_total_uts"] = total_uts
        res_dict["num_compilable_uts"] = num_compilable_uts
        res_dict["num_executed_uts"] = num_executed_uts
        res_dict["num_passed_uts"] = num_passed_uts

        res_dict["method_level_compile_rate"] = (
            num_compilable_uts / total_uts if total_uts != 0 else 0
        )
        res_dict["method_level_executable_rate"] = (
            num_executed_uts / num_compilable_uts if num_compilable_uts != 0 else 0
        )
        res_dict["method_level_pass_rate"] = (
            num_passed_uts / num_compilable_uts if num_compilable_uts != 0 else 0
        )

        # 记录测试执行的结果
        res_dict["fixed_execution_result"] = compile_res["second_compile_res"][
            "coverage_results"
        ]["fixed_passed"]
        res_dict["buggy_execution_result"] = compile_res["second_compile_res"][
            "coverage_results"
        ]["buggy_passed"]

        if (
                compile_res["second_compile_res"]["compiled"]
                and not res_dict["is_empty_test"]
        ):
            res_dict["fixed_execution_error_types"] = compile_res["second_compile_res"][
                "coverage_results"
            ]["fixed_error_types"]
            res_dict["fixed_execution_error_info"] = compile_res["second_compile_res"][
                "coverage_results"
            ]["fixed_error_info"]
        else:
            res_dict["fixed_execution_error_types"] = ["not compiled"]
            res_dict["fixed_execution_error_info"] = ["not compiled"]

        # 记录一下测试类
        res_dict["first_test_content"] = compile_res["first_test_class"]
        res_dict["second_test_content"] = compile_res["second_test_class"]

        second_round_coverage_res = compile_res["second_compile_res"][
            "coverage_results"
        ]

        try:
            second_cov_res = calculate_coverage_stats(
                focal_method,
                second_round_coverage_res["fixed_coverage"],
                method_name,
                package_dir,
                clazz_dir,
                parameter_tuple,
            )
            # 收集第二轮的行覆盖
            cur_covered_lines = second_cov_res["line_coverage_covered"]
            cur_missed_lines = second_cov_res["line_coverage_missed"]
            res_dict["covered_lines"] = cur_covered_lines
            res_dict["missed_lines"] = cur_missed_lines
            # 收集第二轮的分支覆盖
            cur_covered_branches = second_cov_res["branch_coverage_covered"]
            cur_missed_branches = second_cov_res["branch_coverage_missed"]
            res_dict["missed_branches"] = cur_missed_branches
            res_dict["covered_branches"] = cur_covered_branches
        except MethodNotFoundInJacocoException as e:
            print(f"ERROR: {str(e)}")
            res_dict["exception"] = str(e)
            res_dict["covered_lines"] = -1
            res_dict["missed_lines"] = -1
            pass
        except ParameterNotFoundException as e:
            res_dict["exception"] = str(e)
            res_dict["covered_lines"] = -1
            res_dict["missed_lines"] = -1
            print(f"ERROR: {str(e)}")
            pass
    except EmptyTestClassFailedCompileException as e:
        res_dict["exception"] = str(e)
        res_dict["retry_times"] = 100
        res_dict["is_empty_test"] = True
        res_dict["first_compile_res"] = "failed"
        res_dict["second_compile_res"] = "failed"

        res_dict["first_compile_error"] = "EmptyTestClassFailedCompileException"
        res_dict["second_compile_error"] = "EmptyTestClassFailedCompileException"
        res_dict["num_total_uts"] = 0
        res_dict["num_compilable_uts"] = 0
        res_dict["num_executed_uts"] = 0
        res_dict["num_passed_uts"] = 0
        res_dict["method_level_compile_rate"] = 0
        res_dict["method_level_executable_rate"] = 0
        res_dict["method_level_pass_rate"] = 0
        # 记录测试执行的结果
        res_dict["fixed_execution_result"] = False
        res_dict["buggy_execution_result"] = False

        res_dict["fixed_execution_error_types"] = ["not compiled"]
        res_dict["fixed_execution_error_info"] = ["not compiled"]

        # 记录一下测试类
        res_dict["first_test_content"] = ""
        res_dict["second_test_content"] = ""
        res_dict["exception"] = str(e)
        res_dict["covered_lines"] = -1
        res_dict["missed_lines"] = -1

        print(str(e))

    return res_dict
