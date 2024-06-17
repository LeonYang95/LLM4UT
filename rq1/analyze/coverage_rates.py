import os.path
import sys
from datetime import datetime

sys.path.extend(['.', '..'])
import json
import pandas
from data.configuration import output_base_dir, code_base
from collections import Counter


def report_coverages(in_file, ignores):
    """
    计算覆盖率信息
    Args:
        in_file: rq1.py 生成的输出文件

    Returns:
        dict: 返回值是一个字典，包含以下内容：
             {
                "total_covered_lines": 总计覆盖的行数，包含了能够编译和不能够编译的测试类,
                "total_missed_lines": 总计未覆盖的行数，,
                "total_covered_branches": 总计覆盖的分支数，
                "total_missed_branches": 总计未覆盖的分支数,
                "compilable_covered_lines": 能够通过编译的测试用例覆盖的行数,
                "compilable_missed_lines": 能够通过编译的测试用例未覆盖的行数,
                "compilable_covered_branches": 能够通过编译的测试用例覆盖的分支数,
                "compilable_missed_branches": 能够通过编译的测试用例未覆盖的分支数,
                "missed_reasons": 未通过编译的测试用例的原因，是一个 Counter 对象，包含了各种原因的计数
             }
    """
    if not os.path.exists(in_file):
        raise FileNotFoundError(f"File {in_file} not found.")
        pass
    else:
        compilable_covered_lines = 0
        compilable_missed_lines = 0
        compilable_covered_branches = 0
        compilable_missed_branches = 0
        total_covered_lines = 0
        total_missed_lines = 0
        total_covered_branches = 0
        total_missed_branches = 0
        missed_reasons = Counter()

        with open(in_file, 'r', encoding='utf8') as reader:
            for line in reader.readlines():
                line = line.strip()
                instance = json.loads(line)
                if instance['index'] in ignores:
                    continue
                if 'exception' in instance.keys() and instance['exception']:
                    if instance['exception'].startswith("Parameter tuple") and instance['exception'].endswith(
                            'not found.'):
                        missed_reasons['parameter tuple not found'] += 1
                    elif instance['exception'].startswith("ERROR") and instance['exception'].endswith(
                            'failed compilation even though was given an empty test class.'):
                        # 'ERROR: Mockito_11 failed compilation even though was given an empty test class.'
                        missed_reasons['failed in empty test class'] += 1
                    else:
                        raise NotImplementedError(f"Exception {instance['exception']} can not be handled yet.")

                elif instance['num_compilable_uts'] != 0 and not instance['is_empty_test']:
                    missed_reasons['success'] += 1
                    compilable_covered_lines += instance['covered_lines']
                    total_covered_lines += instance['covered_lines']
                    compilable_missed_lines += instance['missed_lines']
                    total_missed_lines += instance['missed_lines']
                    missed_branches = instance['missed_branches']
                    covered_branches = instance['covered_branches']
                    if missed_branches != -1 and covered_branches != -1:
                        compilable_covered_branches += covered_branches
                        compilable_missed_branches += missed_branches
                        total_missed_branches += missed_branches
                        total_covered_branches += covered_branches
                        pass
                else:
                    assert instance['covered_lines'] != -1
                    total_covered_lines += instance['covered_lines']
                    total_missed_lines += instance['missed_lines']
                    missed_branches = instance['missed_branches']
                    covered_branches = instance['covered_branches']
                    if missed_branches != -1 and covered_branches != -1:
                        total_missed_branches += missed_branches
                        total_covered_branches += covered_branches
                        pass

                    missed_reasons['cannot compile'] += 1
                    continue

        return {
            "total_covered_lines": total_covered_lines,
            "total_missed_lines": total_missed_lines,
            "total_covered_branches": total_covered_branches,
            "total_missed_branches": total_missed_branches,
            "compilable_covered_lines": compilable_covered_lines,
            "compilable_missed_lines": compilable_missed_lines,
            "compilable_covered_branches": compilable_covered_branches,
            "compilable_missed_branches": compilable_missed_branches,
            "missed_reasons": missed_reasons
        }


def init_ignore_dict(in_file):
    ignores = set()
    with open(in_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            data = json.loads(line.strip())
            if data['completion'] == '':
                ignores.add(data['index'])
    return ignores


if __name__ == '__main__':
    from data.configuration import target_models, projects, ablations, strategies, formats

    data = {
        "model": [],
        "project": [],
        "ablation": [],
        "total_covered_lines": [],
        "total_missed_lines": [],
        "total_covered_branches": [],
        "total_missed_branches": [],
        "total_line_coverage": [],
        "total_branch_coverage": [],
        "total_lines": [],
        "total_branches": [],
        "compilable_covered_lines": [],
        "compilable_missed_lines": [],
        "compilable_covered_branches": [],
        "compilable_missed_branches": [],
        "compilable_line_coverage": [],
        "compilable_branch_coverage": [],

        "error_reasons": []
    }
    current_datetime = datetime.now()
    # time_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    time_str = current_datetime.strftime("%Y-%m-%d")
    filename = f"coverage_rate_summary_{time_str}.csv"  # 例如 "2023-04-12_14-30-45.txt"
    filename = os.path.join(code_base, f'data/rq1/{filename}')

    for model in target_models:
        for strategy in strategies:  # generation or extend
            ignores = {}
            for ablation in ablations:
                for f in formats:  # comment or natural
                    project_missed_reasons = Counter()
                    project_total_covered_lines = 0
                    project_total_lines = 0
                    project_total_covered_branches = 0
                    project_total_branches = 0

                    project_compilable_covered_lines = 0
                    project_compilable_total_lines = 0
                    project_compilable_covered_branches = 0
                    project_compilable_total_branches = 0
                    for project in projects:
                        in_file = f"{project}_{f}_{strategy}_{ablation}.jsonl"
                        in_file = os.path.join(output_base_dir, f'{model}/{in_file}')
                        if ablation == 'full':
                            ignores[project] = init_ignore_dict(in_file)
                        if not os.path.exists(in_file):
                            continue
                        res = report_coverages(in_file, ignores[project])

                        # 从返回字典中读取数据
                        covered_lines = res['total_covered_lines']
                        total_lines = res['total_covered_lines'] + res['total_missed_lines']
                        covered_branches = res['total_covered_branches']
                        total_branches =res['total_covered_branches'] + res['total_missed_branches']
                        compilable_covered_line = res['compilable_covered_lines']
                        compilable_total_lines = compilable_covered_line + res['compilable_missed_lines']
                        compilable_covered_branches = res['compilable_covered_branches']
                        compilable_total_branches = compilable_covered_branches+res['compilable_missed_branches']

                        # 记录数据
                        project_total_covered_lines += covered_lines
                        project_total_lines += total_lines
                        project_total_covered_branches += covered_branches
                        project_total_branches += total_branches
                        missed_reasons = res['missed_reasons']
                        project_compilable_covered_lines += compilable_covered_line
                        project_compilable_total_lines += compilable_total_lines
                        project_compilable_total_branches += compilable_total_branches
                        project_compilable_covered_branches += compilable_covered_branches
                        project_missed_reasons.update(missed_reasons)

                        total_line_coverage = covered_lines/total_lines
                        total_branch_coverage = covered_branches/total_branches

                        line_coverage = compilable_covered_line/compilable_total_lines
                        branch_coverage = compilable_covered_branches/compilable_total_branches

                        # 记录csv数据
                        data['model'].append(model)
                        data['project'].append(project)
                        data['ablation'].append(ablation)
                        data['total_covered_lines'].append(covered_lines)
                        data['total_missed_lines'].append(-1)
                        data['total_lines'].append(total_lines)
                        data['total_line_coverage'].append(total_line_coverage)
                        data['total_covered_branches'].append(covered_branches)
                        data['total_missed_branches'].append(-1)
                        data['total_branches'].append(total_branches)
                        data['total_branch_coverage'].append(total_branch_coverage)
                        data['compilable_covered_lines'].append(compilable_covered_line)
                        data['compilable_missed_lines'].append(-1)
                        data['compilable_line_coverage'].append(line_coverage)
                        data['compilable_covered_branches'].append(compilable_covered_branches)
                        data['compilable_missed_branches'].append(-1)
                        data['compilable_branch_coverage'].append(branch_coverage)
                        data['error_reasons'].append(str(dict(missed_reasons.most_common())))

                        print('=' * 40)
                        print(f'{project}_{f}_{strategy}_{ablation}:')
                        print(
                            f"Total Line coverage: {covered_lines} / {total_lines} = {total_line_coverage}")
                        print(
                            f"Total Branch coverage: {covered_branches} / {total_branches} = {total_branch_coverage}")
                        print(
                            f"Compilable Line coverage: {compilable_covered_line} / {compilable_total_lines} = {line_coverage}")
                        print(
                            f"Compilable Branch coverage: {compilable_covered_branches} / {compilable_total_branches} = {branch_coverage}")
                        print(f"Missed reasons: {str(dict(missed_reasons.most_common()))}")
                        print('=' * 40)
                        pass
                    print('=' * 20 + 'Model Summary' + '=' * 20)
                    print(f'{model}:')
                    model_compilable_line_coverage = project_compilable_covered_lines/project_compilable_total_lines

                    model_compilable_branch_coverage = project_compilable_covered_branches/project_compilable_total_branches
                    model_total_line_coverage =  project_total_covered_lines /project_total_lines

                    model_total_branch_coverage = project_total_covered_branches/project_total_branches
                    # 记录csv数据
                    data['model'].append(model)
                    data['project'].append('all')
                    data['ablation'].append(ablation)
                    data['total_covered_lines'].append(project_total_covered_lines)
                    data['total_missed_lines'].append(-1)
                    data['total_lines'].append(project_total_lines)
                    data['total_line_coverage'].append(model_total_line_coverage)
                    data['total_covered_branches'].append(project_total_covered_branches)
                    data['total_branches'].append(project_total_branches)
                    data['total_missed_branches'].append(-1)
                    data['total_branch_coverage'].append(model_total_branch_coverage)
                    data['compilable_covered_lines'].append(project_compilable_covered_lines)
                    data['compilable_missed_lines'].append(-1)
                    data['compilable_line_coverage'].append(model_compilable_line_coverage)
                    data['compilable_covered_branches'].append(project_compilable_covered_branches)
                    data['compilable_missed_branches'].append(-1)
                    data['compilable_branch_coverage'].append(model_compilable_branch_coverage)
                    data['error_reasons'].append(str(dict(project_missed_reasons.most_common())))
                    print(
                        f"Total Line coverage: {project_total_covered_lines} / {project_total_lines} = {model_total_line_coverage}")
                    print(
                        f"Total Branch coverage: {project_total_covered_branches} / {project_total_branches} = {model_total_branch_coverage}")
                    print(
                        f"Compilable Line coverage: {project_compilable_covered_lines} / {project_compilable_total_lines} = {model_compilable_line_coverage}")
                    print(
                        f"Compilable Branch coverage: {project_compilable_covered_branches} / {project_compilable_total_branches} = {model_compilable_branch_coverage}")
                    print(f"Missed reasons: {str(dict(project_missed_reasons.most_common()))}")
                    print('=' * 40)

    df = pandas.DataFrame(data)
    df.to_csv(filename, index=False)
