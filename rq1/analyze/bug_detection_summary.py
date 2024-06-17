import os.path
import sys
from datetime import datetime

sys.path.extend(['.', '..'])
import json
import pandas
from data.configuration import output_base_dir, code_base


def report_bug_detection_results(in_file):
    attempts = set()
    found = set()
    if not os.path.exists(in_file):
        print(f"ERROR: File {in_file} not found.")
        pass
    else:
        with open(in_file, 'r', encoding='utf8') as reader:
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                fixed_passed = instance['fixed_execution_result']
                buggy_passed = instance['buggy_execution_result']
                if fixed_passed and instance['fixed_execution_error_info'][0] != 'not compiled':
                    if not instance['is_empty_test']:
                        attempts.add(instance['bug_id'])
                        if not buggy_passed:
                            found.add(instance['bug_id'])
                        pass
                    else:
                        continue
        return {
            "found_bugs": found,
            "attempts": attempts
        }


if __name__ == '__main__':
    from data.configuration import target_models, projects, ablations, strategies, formats

    data = {
        "model": [],
        "project": [],
        "ablation": [],
        "num_bugs_found": [],
        "num_attempts": [],
        "found_bugs": [],
        "attempts": []
    }
    current_datetime = datetime.now()
    # time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = current_datetime.strftime("%Y-%m-%d")
    filename = f"bug_detection_summary_{time_str}.csv"  # 例如 "2023-04-12_14-30-45.txt"
    filename = os.path.join(code_base, f'data/rq1/{filename}')

    for model in target_models:
        for strategy in strategies:  # generation or extend
            for ablation in ablations:
                for f in formats:  # comment or natural
                    model_found_bugs = set()
                    model_attempts = set()
                    for project in projects:
                        in_file = f"{project}_{f}_{strategy}_{ablation}.jsonl"
                        in_file = os.path.join(output_base_dir, f'{model}/{in_file}')
                        res = report_bug_detection_results(in_file)
                        if not res:
                            continue

                        # 记录csv数据
                        data['model'].append(model)
                        data['project'].append(project)
                        data['ablation'].append(ablation)
                        data['found_bugs'].append(res['found_bugs'])
                        data['attempts'].append(res['attempts'])
                        model_found_bugs |= res['found_bugs']
                        model_attempts |= res['attempts']
                        data['num_bugs_found'].append(len(res['found_bugs']))
                        data['num_attempts'].append(len(res['attempts']))

                        print('=' * 40)
                        print(f'{project}_{f}_{strategy}_{ablation}:')
                        print(f"Found {len(res['found_bugs'])} bugs in {len(res['attempts'])} attempts.")
                        print('=' * 40)
                        pass
                    print('=' * 20 + 'Model Summary' + '=' * 20)
                    print(f'{model}:')
                    # 记录csv数据
                    data['model'].append(model)
                    data['project'].append('all')
                    data['ablation'].append(ablation)
                    data['found_bugs'].append(model_found_bugs)
                    data['attempts'].append(model_attempts)
                    data['num_bugs_found'].append(len(model_found_bugs))
                    data['num_attempts'].append(len(model_attempts))
                    print(f"Found {len(model_found_bugs)} bugs in {len(model_attempts)} attempts.")
                    print('=' * 40)

    df = pandas.DataFrame(data)
    df.to_csv(filename, index=False)
