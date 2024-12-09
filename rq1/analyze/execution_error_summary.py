import os.path
import sys

sys.path.extend(['.', '..'])
import json
import re
import pandas
import pickle
from configuration import output_base_dir, code_base
from collections import Counter
import numpy as np
from datetime import datetime

execution_error_keys = {
    "not compiled": [],
    "java.lang.NullPointerException": [],
    'java.lang.IllegalStateException': [],
    'junit.framework.AssertionFailedError': [],
    'org.mockito.exceptions.base.MockitoException': [],
    'java.lang.ArithmeticException': [],
    "pass": [],
    'java.lang.NumberFormatException': [],
    'java.lang.IllegalArgumentException': [],
    'java.lang.ArrayIndexOutOfBoundsException': [],
    'java.lang.IndexOutOfBoundsException': [],
    'java.lang.UnsupportedOperationException': [],
    'java.lang.ClassCastException': [],
    'org.apache.commons.*': [],
    'java.util.NoSuchElementException': [],
    'java.lang.Exception: No runnable': [],
    'java.lang.StringIndexOutOfBoundsException': [],
    'java.lang.NegativeArraySizeException': [],
    'java.lang.Exception: Unexpected exception': [],
    'org.mockito.exceptions.misusing.MissingMethodInvocationException': [],
    'org.jfree.*': [],
    '.invoke\(PluginLoader': [],
}


def reset():
    global execution_error_keys
    for key in execution_error_keys.keys():
        execution_error_keys[key].clear()


def update_execution_error_info(in_file):
    project_compile_err_keys = pickle.loads(pickle.dumps(execution_error_keys))
    if not os.path.exists(in_file):
        print(f"ERROR: File {in_file} not found.")
        pass
    else:
        with open(in_file, 'r', encoding='utf8') as reader:
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                index = f"{instance['project']}_{instance['index']}"

                if instance['fixed_execution_error_types'] == ['success'] or instance['fixed_execution_error_types'] == ['not compiled']:
                    pass
                else:
                    err_msg_lines = instance['fixed_execution_error_types']
                    for msg_line in err_msg_lines:
                        for key, _ in project_compile_err_keys.items():
                            if re.match(key, msg_line):
                                project_compile_err_keys[key].append(index)
                                break

    return project_compile_err_keys




if __name__ == '__main__':
    from configuration import target_models, projects, ablations, strategies, formats

    current_datetime = datetime.now()
    # time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = current_datetime.strftime("%Y-%m-%d")
    filename = f"execution_error_effect_size_summary_{time_str}.csv"  # 例如 "2023-04-12_14-30-45.txt"
    filename = os.path.join(code_base, f'data/rq1/{filename}')
    df = {
        "model": [],
        "project": [],
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
                    project_execution_err_types = Counter()
                    reset()
                    for project in projects:
                        in_file = f"{project}_{f}_{strategy}_{ablation}.jsonl"
                        in_file = os.path.join(output_base_dir, f'{model}/{in_file}')
                        if not os.path.exists(in_file):
                            continue

                        execiton_errors = update_execution_error_info(in_file)
                        df['model'].append(f"{model}_{f}_{strategy}_{ablation}")
                        df['project'].append(project)
                        project_execution_err_types.update(execiton_errors)
                        total = np.sum([len(set(affected_list)) for _, affected_list in execiton_errors.items()])
                        for key, affected_list in execiton_errors.items():
                            # df[key].append(len(set(affected_list)))
                            if total == 0:
                                affect_rate = 0
                            else:
                                affect_rate = len(set(affected_list)) / total
                            df[f"{key}_ratio"].append(affect_rate)
                            execution_error_keys[key].extend(affected_list)

                    # **************************************************************************************************
                    # 收集compile_error_key的逻辑，别删
                    # filtered_compile_err = Counter()
                    # unmatched = False
                    #
                    # for err, count in project_execution_err_types.most_common():
                    #     if count <= 1:
                    #         print(err)
                    #         break
                    #     if any(re.match(key, err) for key, _ in compile_err_keys.items()):
                    #         continue
                    #     else:
                    #         unmatched = True
                    #         break
                    # if unmatched:
                    #     print(err)
                    # **************************************************************************************************
                    df['model'].append(f"{model}_{f}_{strategy}_{ablation}")
                    df['project'].append('all')
                    project_total = np.sum([len(set(affected_list)) for _, affected_list in execution_error_keys.items()])
                    for key, affected_list in execution_error_keys.items():
                        # df[key].append(len(set(affected_list)))
                        if project_total == 0:
                            affect_rate = 0
                        else:
                            affect_rate = len(set(affected_list)) / project_total
                        df[f"{key}_ratio"].append(affect_rate)

    pd = pandas.DataFrame(df)
    pd.to_csv(filename, index=False)
