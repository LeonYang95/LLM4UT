import json
import os

from rq1.assistant_methods import analyze_method_signature_for_coverage
from parse_evosuite_xml import parse_coverage_xml
from utils.exceptions import MethodNotFoundInJacocoException, ParameterNotFoundException
from utils.java_parser import has_branch

# Define Global Variables
RESULTS_DIR = "data/rq1"

OUTPUT_BASE = 'data/rq1/results_evo'

EVO_DIR = "baselines/evosuite_coverages/coverage_log"

RULER_INPUT_BASE = 'data/rq1/results_0128'

projects = [
    "JxPath",
    "Cli",
    "Math",
    "Csv",
    "Compress",
    "JacksonDatabind",
    "Time",
    "Collections",
    "JacksonXml",
    # "Mockito",
    "JacksonCore",
    "Lang",
    "Jsoup",
    "Chart",
    "Gson",
    "Closure",
    "Codec"
]


def evoSignatureExtractor(s):
    sig = s[1:].split(')')[0]
    if len(sig) == 0:
        # 返回空集合
        return ()
    else:
        sig = sig.strip(';').replace('/', '.').split(';')
        sig = [x.split('L')[-1].lower() for x in sig]
        return tuple(sig)


def getCov(path, data):
    ms = data['method_signature']
    focal_method = data['focal_method']

    (
        ori_package_name,
        ori_package_dir,
        ori_class_name,
        ori_clazz_dir,
        ori_method_name,
        ori_parameter_tuple,
    ) = analyze_method_signature_for_coverage(ms)

    res_dict = {}

    # 解析XML文件
    coverage_data = parse_coverage_xml(path)
    try:
        second_cov_res = calculate_coverage_stats(
            focal_method,
            coverage_data,
            ori_method_name,
            ori_package_dir.replace('/', '.'),
            ori_clazz_dir.replace('/', '.'),
            ori_parameter_tuple,
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

    return res_dict


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
            # print("数据格式有问题，重新寻找")
            md = fixed_coverage_data[package_dir][clazz_dir][method_name]
            new_md = {}
            for k in md.keys():
                new_md[tuple([x.replace("$", '.') for x in k])] = md[k]
            focal_method_cov = new_md.get(
                parameter_tuple, None
            )

        if focal_method_cov is None:
            raise ParameterNotFoundException(
                f"Parameter tuple {parameter_tuple} not found."
            )

        if focal_method_cov["line_coverage"] is not None:
            res_dict["line_coverage_covered"] = int(
                focal_method_cov["line_coverage"]["covered_lines"]
            )
            res_dict["line_coverage_missed"] = int(
                focal_method_cov["line_coverage"]["missed_lines"]
            )
        if focal_method_cov["branch_coverage"] is not None and has_branch(focal_method):
            res_dict["branch_coverage_covered"] = int(
                focal_method_cov["branch_coverage"]["covered_branches"]
            )
            res_dict["branch_coverage_missed"] = int(
                focal_method_cov["branch_coverage"]["missed_branches"]
            )

    else:
        raise MethodNotFoundInJacocoException(
            f"method {method_name} not found in {package_dir}/{clazz_dir}"
        )

    return res_dict


def main():
    if not os.path.exists(OUTPUT_BASE):
        os.makedirs(OUTPUT_BASE, exist_ok=True)

    # 行覆盖率数组
    total_covered_lines = []
    total_missed_lines = []
    # 分支覆盖率数组
    total_covered_branches = []
    total_missed_branches = []
    for project in projects:
        ruler_inputs = f"{RULER_INPUT_BASE}/Phind-CodeLlama-34B-v2/{project}_comment_extend_full.jsonl"
        if os.path.exists(ruler_inputs):
            with open(ruler_inputs, "r") as file:
                analyze_res_writer = open(
                    f"{OUTPUT_BASE}/{project}.jsonl",
                    "w",
                    encoding="utf-8",
                )
                for line in file.readlines():
                    data = json.loads(line)
                    bug_id = data["bug_id"]
                    id = bug_id.split('_')[1]
                    coverage_file = f"{EVO_DIR}/{project}/evosuite/{id}f.1.xml"
                    if os.path.exists(coverage_file):
                        res_dict = getCov(coverage_file, data)
                        # res_dict["ablation"] = ablation
                        res_dict["id"] = bug_id
                        # res_dict["strategy"] = strategy
                        # res_dict["format"] = format
                        res_dict["class_name"] = data['class_name']
                        res_dict["method_signature"] = data['method_signature']
                        res_dict["focal_method"] = data["focal_method"]
                        res_dict['index'] = data['index']
                        res_dict['project'] = data['project']

                        if 'exception' in res_dict.keys() or res_dict['covered_lines'] == -1:
                            continue

                        # 计算覆盖率
                        if res_dict["covered_branches"] == -1:
                            pass
                        else:
                            total_covered_branches.append(res_dict["covered_branches"])
                            total_missed_branches.append(res_dict["missed_branches"])
                        if res_dict["covered_lines"] == -1:
                            pass
                        else:
                            total_covered_lines.append(res_dict["covered_lines"])
                            total_missed_lines.append(res_dict["missed_lines"])

                        analyze_res_writer.write(json.dumps(res_dict) + "\n")
                    else:
                        pass
                        # print("EVO 数据不存在")

                analyze_res_writer.flush()
                analyze_res_writer.close()


        else:
            print("Coverage file does not exist: " + ruler_inputs)

    # 计算平均值
    # 输出行覆盖率
    if sum(total_covered_lines) + sum(total_missed_lines) != 0:
        print(
            f"Total covered lines: {sum(total_covered_lines) / (sum(total_covered_lines) + sum(total_missed_lines))}")
    else:
        print(f"Total covered lines: 0")
    # 输出分支覆盖率
    if sum(total_covered_branches) + sum(total_missed_branches) != 0:
        print(
            f"Total covered branches: {sum(total_covered_branches) / (sum(total_covered_branches) + sum(total_missed_branches))}")
    else:
        print(f"Total covered branches: 0")


if __name__ == "__main__":
    main()
