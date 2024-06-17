import os.path
import sys

sys.path.extend(['.', '..'])
import json
import re
import pandas
import pickle
from data.configuration import output_base_dir, code_base
from collections import Counter

from datetime import datetime

ignore_index = set()
ignore_index_file = os.path.join(code_base, 'data/base_ignore_index.pkl')
if os.path.exists(ignore_index_file):
    with open(ignore_index_file, 'rb') as reader:
        ignore_index = pickle.load(reader)


def report_compile_rate(in_file):
    """
    计算编译率信息
    Args:
        in_file: rq1.py跑出来的目标结果文件

    Returns:
        compile_classes: 编译成功的类数
        total_classes: 总类数
        compile_uts: 编译成功的测试用例数
        total_uts: 总测试用例数
        compile_errs: 编译错误信息统计（Counter）
    """
    if not os.path.exists(in_file):
        print(f"ERROR: File {in_file} not found.")
        return None, None, None, None, None
        pass
    else:
        compile_classes = 0
        compile_uts = 0
        total_classes = 0
        total_uts = 0
        with open(in_file, 'r', encoding='utf8') as reader:
            compile_errs = Counter()
            idx = 0
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                if idx in ignore_index or instance['completion'] == 'out of max_tokens' or instance['completion'] == "":
                    if id not in ignore_index:
                        ignore_index.add(idx)
                    continue

                total_classes += 1
                total_uts += instance['num_total_uts']

                if instance['first_compile_res'] == 'success':
                    compile_classes += 1
                    pass
                else:
                    err_msg_lines = instance['first_compile_error'].split('\n')
                    pattern = r'error: (.*)'
                    for msg_line in err_msg_lines:
                        match = re.search(pattern, msg_line)
                        if match:
                            compile_errs[match.group(1)] += 1

                if instance['second_compile_res'] and not instance['is_empty_test']:
                    compile_uts += instance['num_compilable_uts']
                    pass

                idx += 1
        if not os.path.exists(ignore_index_file):
            with open(ignore_index_file, 'wb') as writer:
                pickle.dump(ignore_index, writer)
        return compile_classes, total_classes, compile_uts, total_uts, compile_errs



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
        with open(in_file, 'r', encoding='utf8') as reader:
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                executable_uts += instance['num_executed_uts']
                passed_uts += instance['num_passed_uts']
                compile_uts += instance['num_compilable_uts']
                execution_errors.update(instance['fixed_execution_error_types'])

        return passed_uts, executable_uts, compile_uts, execution_errors


if __name__ == '__main__':
    from data.configuration import target_models, projects, ablations, strategies, formats

    current_datetime = datetime.now()
    # time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = current_datetime.strftime("%Y-%m-%d")
    filename = f"compile_rate_summary_{time_str}.csv"  # 例如 "2023-04-12_14-30-45.txt"
    filename = os.path.join(code_base, f'data/rq1/{filename}')
    df = {
        "model": [],
        "project": [],
        "ablation": [],
        "strategy": [],
        "compilable_classes": [],
        "total_classes": [],
        "class_level_compile_rate": [],
        "total_uts": [],
        "compilable_uts": [],
        "method_level_compile_rate": [],
        "executable_uts": [],
        "executable_rate": [],
        "passed_uts": [],
        "pass_rate": [],
        "compilation_errors": [],
        "execution_errors": []
    }
    for model in target_models:
        for strategy in strategies:  # generation or extend
            for ablation in ablations:
                for f in formats:  # comment or natural
                    num_compiled_classes = 0
                    num_all_classes = 0
                    num_compiled_uts = 0
                    num_all_uts = 0
                    num_executable_uts = 0
                    num_passed_uts = 0
                    compile_err_types = Counter()
                    execution_err_types = Counter()
                    for project in projects:
                        in_file = f"{project}_{f}_{strategy}_{ablation}.jsonl"
                        in_file = os.path.join(output_base_dir, f'{model}/{in_file}')
                        if not os.path.exists(in_file):
                            continue
                        compile_classes, total_classes, compile_uts, total_uts, compile_errs = report_compile_rate(
                            in_file)
                        if total_classes is None:
                            continue
                        class_level_rate = compile_classes / total_classes if total_classes != 0 else 0
                        method_level_rate = compile_uts / total_uts if total_uts != 0 else 0
                        num_all_classes += total_classes
                        num_compiled_classes += compile_classes
                        num_all_uts += total_uts
                        num_compiled_uts += compile_uts
                        compile_err_types.update(compile_errs)

                        passed_uts, executable_uts, tmp, execution_errors = report_execution_rates(in_file)
                        assert tmp == compile_uts
                        num_executable_uts += executable_uts
                        num_passed_uts += passed_uts
                        execution_err_types.update(execution_errors)

                        executable_rate = executable_uts / compile_uts if compile_uts != 0 else 0
                        pass_rate = passed_uts / executable_uts if executable_uts != 0 else 0
                        df['model'].append(f"{model}")
                        df['ablation'].append(ablation)
                        df['project'].append(project)
                        df['strategy'].append(strategy)
                        df['compilable_classes'].append(compile_classes)
                        df['total_classes'].append(total_classes)
                        df['class_level_compile_rate'].append(class_level_rate)
                        df['total_uts'].append(total_uts)
                        df['compilable_uts'].append(compile_uts)
                        df['method_level_compile_rate'].append(method_level_rate)
                        df['executable_uts'].append(executable_uts)
                        df['executable_rate'].append(executable_rate)
                        df['passed_uts'].append(passed_uts)
                        df['pass_rate'].append(pass_rate)
                        df['compilation_errors'].append(str(dict(compile_errs.most_common())))
                        df['execution_errors'].append(str(dict(execution_errors.most_common())))
                        print('=' * 40)
                        print(f'{project}_{f}_{strategy}_{ablation}:')
                        print(f'Class level compile rate: {compile_classes} / {total_classes} = {class_level_rate}')
                        print(f'Method level compile rate: {compile_uts}/{total_uts} = {method_level_rate}')
                        print(f'Compile errors: {str(dict(compile_errs.most_common()))}')
                        print(f'Executable rate: {executable_uts}/{compile_uts} = {executable_rate}')
                        print(f'Pass rate: {passed_uts}/{executable_uts} = {pass_rate}')
                        print(f'Execution errors: {str(dict(execution_errors.most_common()))}')
                        print('=' * 40)
                        pass
                    print('=' * 20 + 'Model Summary' + '=' * 20)
                    print(f'{model}:')
                    model_class_level_compile_rate = num_compiled_classes / num_all_classes if num_all_classes != 0 else 0
                    model_method_level_compile_rate = num_compiled_uts / num_all_uts if num_all_uts != 0 else 0
                    model_executable_rate = num_executable_uts / num_compiled_uts if num_compiled_uts != 0 else 0
                    model_passed_rate = num_passed_uts / num_executable_uts if num_executable_uts != 0 else 0
                    df['model'].append(model)
                    df['project'].append('all')
                    df['strateg=y'].append(strategy)
                    df['ablation'].append(ablation)
                    df['compilable_classes'].append(num_compiled_classes)
                    df['total_classes'].append(num_all_classes)
                    df['class_level_compile_rate'].append(model_class_level_compile_rate)
                    df['total_uts'].append(num_all_uts)
                    df['compilable_uts'].append(num_compiled_uts)
                    df['method_level_compile_rate'].append(model_method_level_compile_rate)
                    df['executable_uts'].append(num_executable_uts)
                    df['executable_rate'].append(model_executable_rate)
                    df['passed_uts'].append(num_passed_uts)
                    df['pass_rate'].append(model_passed_rate)
                    df['compilation_errors'].append(str(dict(compile_err_types.most_common())))
                    df['execution_errors'].append(str(dict(execution_err_types.most_common())))
                    print(
                        f'Class level compile rate: {num_compiled_classes} / {num_all_classes} = {model_class_level_compile_rate}')
                    print(
                        f'Method level compile rate: {num_compiled_uts}/{num_all_uts} = {model_method_level_compile_rate}')
                    print(f'Executable rate: {num_executable_uts}/{num_compiled_uts} = {model_executable_rate}')
                    print(f'Pass rate: {num_passed_uts}/{num_executable_uts} = {model_passed_rate}')
                    print(f'Compile errors: {str(dict(compile_err_types.most_common()))}')
                    print(f'Execution errors: {str(dict(execution_err_types.most_common()))}')
                    print('=' * 40)

    pd = pandas.DataFrame(df)
    pd.to_csv(filename, index=False)
