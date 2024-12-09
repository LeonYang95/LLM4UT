import os.path
import sys

sys.path.extend([".", ".."])
import json
import re
import pandas
from configuration import output_base_dir, code_base
from collections import Counter
from datetime import datetime

execution_error_keys = {
    "cannot find symbol": [],
    "incompatible types": [],
    "(.*) is abstract; cannot be instantiated": [],
    "(.*) has private access in (.*)": [],
    "'void' type not allowed here": [],
    "no suitable (constructor|method) found for (.*)": [],
    "constructor (.*) in class (.*) cannot be applied to given types": [],
    "non-static (variable|method) (.*) cannot be referenced from a static context": [],
    "method (.*) in class (.*) cannot be applied to given types": [],
    "reference to (.*) is ambiguous": [],
    "unreported exception (.*); must be caught or declared to be thrown": [],
    "cannot assign a value to final": [],
    "(empty|unclosed) character literal": [],
    "integer number too large": [],
    "void cannot be dereferenced": [],
    "possible loss of precision": [],
    "method does not override or implement a method from a supertype": [],
    "illegal start of expression": [],
    r"(';'|'\)') expected": [],
    "not a statement": [],
    "(.*) has protected access in (.*)": [],
    "bad operand type (.*) for (binary|unary) operator (.*)": [],
    "(.*) is not abstract and does not override abstract method (.*) in (.*)": [],
    "exception (.*) is never thrown in body of corresponding try statement": [],
    "local variable series is accessed from within inner class; needs to be declared final": [],
    "package (.*) does not exist": [],
    "method (.*) in interface (.*) cannot be applied to given types;": [],
    "variable (.*) is already defined in class (.*)": [],
    "enum types may not be instantiated": [],
    "unexpected type": [],
    "cannot infer type arguments for (.*)": [],
    "an enclosing instance that contains (.*) is required": [],
}


def reset():
    global execution_error_keys
    for key in execution_error_keys.keys():
        execution_error_keys[key].clear()


def update_compile_err_classification(in_file):
    """
    Update the classification of compile errors based on the given input file.

    Args:
        in_file (str): The path to the input file.

    Returns:
        dict: A dictionary containing the classification of compile errors. The keys are the error types,
              and the values are lists of project and index pairs where the corresponding error occurred.
    """
    project_compile_err_keys = {
        "cannot find symbol": set(),
        "incompatible types": set(),
        "(.*) is abstract; cannot be instantiated": set(),
        "(.*) has private access in (.*)": set(),
        "'void' type not allowed here": set(),
        "no suitable (constructor|method) found for (.*)": set(),
        "constructor (.*) in class (.*) cannot be applied to given types": set(),
        "non-static (variable|method) (.*) cannot be referenced from a static context": set(),
        "method (.*) in class (.*) cannot be applied to given types": set(),
        "reference to (.*) is ambiguous": set(),
        "unreported exception (.*); must be caught or declared to be thrown": set(),
        "cannot assign a value to final": set(),
        "(empty|unclosed) character literal": set(),
        "integer number too large": set(),
        "void cannot be dereferenced": set(),
        "possible loss of precision": set(),
        "method does not override or implement a method from a supertype": set(),
        "illegal start of expression": set(),
        r"(';'|'\)') expected": set(),
        "not a statement": set(),
        "(.*) has protected access in (.*)": set(),
        "bad operand type (.*) for (binary|unary) operator (.*)": set(),
        "(.*) is not abstract and does not override abstract method (.*) in (.*)": set(),
        "exception (.*) is never thrown in body of corresponding try statement": set(),
        "local variable series is accessed from within inner class; needs to be declared final": set(),
        "package (.*) does not exist": set(),
        "method (.*) in interface (.*) cannot be applied to given types;": set(),
        "variable (.*) is already defined in class (.*)": set(),
        "enum types may not be instantiated": set(),
        "unexpected type": set(),
        "cannot infer type arguments for (.*)": set(),
        "an enclosing instance that contains (.*) is required": set(),
    }

    if not os.path.exists(in_file):
        raise FileNotFoundError(f"File {in_file} not found.")
    else:
        with open(in_file, "r", encoding="utf8") as reader:
            print(in_file)
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                index = f"{instance['project']}_{instance['index']}"

                if instance["first_compile_res"] == "success":
                    pass
                else:
                    err_msg_lines = instance["first_compile_error"].split("\n")
                    pattern = r"error: (.*)"
                    for msg_line in err_msg_lines:
                        match = re.search(pattern, msg_line)
                        if match:
                            for key in project_compile_err_keys.keys():
                                res = re.match(key, match.group(1))
                                if res:
                                    project_compile_err_keys[key].add(index)

    return project_compile_err_keys


def report_execution_rates(in_file):
    """
    计算执行率信息
    Args:
        in_file: rq1.py跑出来的目标结果文件

    Returns:
        passed_uts: 执行成功的测试用例数
        executable_uts: 可执行的测试用例数
        compile_uts: 编译成功的测试用例数
        execution_errors: 执行错误信息统计（Counter）
    """
    if not os.path.exists(in_file):
        raise FileNotFoundError(f"File {in_file} not found.")
        pass
    else:
        executable_uts = 0
        compile_uts = 0
        passed_uts = 0
        execution_errors = Counter()
        with open(in_file, "r", encoding="utf8") as reader:
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                executable_uts += instance["num_executed_uts"]
                passed_uts += instance["num_passed_uts"]
                compile_uts += instance["num_compilable_uts"]
                execution_errors.update(instance["fixed_execution_error_types"])

        return passed_uts, executable_uts, compile_uts, execution_errors


if __name__ == "__main__":
    from configuration import (
        target_models,
        projects,
        ablations,
        strategies,
        formats,
    )

    current_datetime = datetime.now()
    # time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = current_datetime.strftime("%Y-%m-%d")
    filename = f"compile_error_effect_size_summary_{time_str}.csv"  # 例如 "2023-04-12_14-30-45.txt"
    filename = os.path.join(code_base, f"data/rq1/{filename}")
    df = {
        "model": [],
        "project": [],
        "ablation": []
    }
    for key in execution_error_keys.keys():
        # df[key] = []
        df[f"{key}_ratio"] = []
    execution_err_keys = {}

    for model in target_models:
        for strategy in strategies:  # generation or extend
            for ablation in ablations:
                for f in formats:  # comment or natural
                    compile_err_types = Counter()
                    execution_err_types = Counter()
                    project_total = 0
                    reset()
                    for project in projects:
                        in_file = f"{project}_{f}_{strategy}_{ablation}.jsonl"
                        in_file = os.path.join(output_base_dir, f"{model}/{in_file}")
                        if not os.path.exists(in_file):
                            continue
                        project_compile_err_keys = update_compile_err_classification(
                            in_file
                        )
                        df["model"].append(model)
                        df['ablation'].append(ablation)
                        df["project"].append(project)
                        with open(in_file, "r", encoding="utf8") as reader:
                            content = reader.read()
                            total = len(content.split('\n'))
                        project_total += total
                        # total = np.sum(
                        #     [
                        #         len(set(affected_list))
                        #         for _, affected_list in project_compile_err_keys.items()
                        #     ]
                        # )

                        for key, affected_list in project_compile_err_keys.items():
                            # df[key].append(len(set(affected_list)))
                            if total == 0:
                                affect_rate = 0
                            else:
                                affect_rate = len(set(affected_list)) / total
                            df[f"{key}_ratio"].append(affect_rate)
                            execution_error_keys[key].extend(list(affected_list))

                        # compile_err_types.update(compile_errs)
                        # passed_uts, executable_uts, tmp, execution_errors = report_execution_rates(in_file)
                        # execution_err_types.update(execution_errors)

                    # **************************************************************************************************
                    # 收集compile_error_key的逻辑，别删
                    # filtered_compile_err = Counter()
                    # unmatched = False
                    # for err, count in compile_err_types.most_common():
                    #     if count <= 1:
                    #         print(err)
                    #         break
                    #     if any(re.match(key, err) for key, _ in compile_err_keys.items()):
                    #         continue
                    #     else:
                    #         unmatched = True
                    #         break
                    # **************************************************************************************************
                    df["model"].append(model)
                    df['ablation'].append(ablation)
                    df["project"].append("all")
                    print(project_total)
                    for key, affected_list in execution_error_keys.items():
                        # df[key].append(len(set(affected_list)))
                        if project_total == 0:
                            affect_rate = 0
                        else:
                            affect_rate = len(affected_list) / project_total
                        df[f"{key}_ratio"].append(affect_rate)

    pd = pandas.DataFrame(df)
    pd.to_csv(filename, index=False)
