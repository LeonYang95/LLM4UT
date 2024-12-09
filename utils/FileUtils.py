import pickle
import sys

sys.path.extend(['.', '..'])

from configuration import *


def load_jsonl_file(input_file: str) -> list:
    results = []
    with open(input_file, "r", encoding="utf-8") as reader:
        for line in reader.readlines():
            line = line.strip()
            data = json.loads(line)
            data['project'] = data['id'].split('_')[0]
            data['bug_id'] = '_'.join(data['id'].split('_')[:-1])
            data['focal_method_signature'] = data['method_signature']
            results.append(pickle.loads(pickle.dumps(data)))
    return results


def write_test_class(bug_id, version, content):
    test_file_dir, test_file_path = _get_test_class_path(bug_id, version)
    if not os.path.exists(test_file_dir):
        os.makedirs(test_file_dir)
    with open(test_file_path, "w", encoding="utf-8") as writer:
        writer.write(content)
    pass


def _get_test_class_path(bug_id, version):
    if content_path[bug_id.lower()]["test"][0] != "/":
        test_base = content_path[bug_id.lower()]["test"]
    else:
        test_base = content_path[bug_id.lower()]["test"][1:]
    test_base_dir = os.path.join(d4j_proj_base, bug_id, version, test_base)

    # 单列一个路径，防止影响已有的测试用例
    test_file_dir = os.path.join(str(test_base_dir), 'org/llm')
    res_file_path = os.path.join(str(test_file_dir), "LLMTests.java")
    return test_file_dir, res_file_path
