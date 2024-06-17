import os.path
import sys

sys.path.extend([".", ".."])
import time
from tqdm import tqdm
import json
import cProfile

# from transformers import AutoTokenizer
from utils.java_parser import parse_fields_from_class_code
from data.configuration import code_base
from utils.prompt_formats.prompt_formatter import PromptFormatter

profiler = cProfile.Profile()
focal_method_key = "source:source_method_code_format"
focal_class_fields_key = "source_class_fields"
focal_method_name_key = "source:source_method_name"
focal_method_signature_key = "source:source_method_signature"
focal_class_other_methods_key = "source:source_other_method_signature"
focal_class_constructor_key = "content:source_class_constructors"
focal_class_name_key = "content:source_class_name"
focal_class_code_key = "content:source_class_code_format"
source_method_type_constructor_key = "content:parameter_class_constructors"
source_method_paramter_key = "content:parameter_list"
parameter_classes_key = "content:parameter_class_signature"
source_method_signature_key = "source:source_method_signature"
source_class_imports_key = "content:source_class_code_imports"

if __name__ == "__main__":
    # ablation_idx = int(sys.argv[1])
    ablation_idx = 0
    model_paths = [
        # '/data/public/CodeLlama-7b-hf',
        # '/data/public/CodeLlama-13b-hf',
        # '/data/public/CodeLlama-34b-hf',
        # '/data/public/CodeLlama-7b-Instruct-hf',
        # '/data/public/CodeLlama-13b-Instruct-hf',
        # '/data/public/CodeLlama-34b-Instruct',
        # '/data/public/deepseek-coder-6.7b-instruct',
        # '/data/public/deepseek-coder-33b-instruct',
        # '/data/public/Phind-CodeLlama-34B-v2',
        # '/data/public/starchat-beta',
        # '/data/public/WizardCoder-15B-V1.0',
        # '/data/public/WizardCoder-Python-34B-V1.0'
        # "chatgpt",
        "Gemma-7b-it"
    ]
    formats = [
        # 'natural',
        "comment"
    ]
    strategies = [
        # 'generation',
        "extend"
    ]
    ablation_features = [
        "full",
        # 'no_param',
        # 'no_param_constructor',
        # 'no_class_constructor',
        # 'no_class_fields',
        # 'no_class_other_methods'
    ]
    ablation_features = [ablation_features[ablation_idx]]

    formatter = PromptFormatter()
    data = []
    backup_file = os.path.join(code_base, "data/prompts/source_data.jsonl")
    if os.path.exists(backup_file):
        with open(backup_file, "r", encoding="utf-8") as reader:
            for line in reader.readlines():
                d = json.loads(line.strip())
                data.append(d)
    else:
        # 循环遍历每个bug
        with open(
            os.path.join(code_base, "data/d4j_fixed_project_list"),
            "r",
            encoding="utf-8",
        ) as reader:
            for line in tqdm(reader.readlines(), desc="Loading d4j bugs: "):
                start = time.time()
                infos = line.strip().split("_")
                project_name = infos[0]
                bug_id = "_".join(infos[:2])

                # 读取bug的信息，拿到 modified class 和 method
                with open(
                    os.path.join(
                        code_base,
                        "data/d4j2_fix_info/" + bug_id + "/buggy_fix_info.json",
                    ),
                    "r",
                    encoding="utf-8",
                ) as info_reader:
                    bug_fix_info = json.load(info_reader)

                target = {}
                for change in bug_fix_info["fixing_changes"]:
                    raw_changed_functions = change["changed_functions"][0][
                        "qualified_names"
                    ]
                    for raw_signature in raw_changed_functions:
                        class_name, method_name = raw_signature.split(":")[:2]
                        signature = class_name + "#" + method_name
                        target[class_name] = {method_name: signature}

                # 读取对应采集的文件，筛选source method
                with open(
                    os.path.join(
                        code_base,
                        "data/fixed_projects_source/"
                        + project_name
                        + "/"
                        + bug_id
                        + "_fixed.jsonl",
                    ),
                    "r",
                    encoding="utf-8",
                ) as source_reader:
                    for line in source_reader.readlines():
                        obj = json.loads(line.strip())
                        for key, item in obj.items():
                            source_class_signature = ".".join(
                                item[source_method_signature_key].split("#")[:2]
                            )
                            if source_class_signature not in target.keys():
                                continue
                            target_method = item[focal_method_name_key]
                            if (
                                target_method
                                not in target[source_class_signature].keys()
                            ):
                                continue
                            data.append(item)

        with open(backup_file, "w", encoding="utf-8") as writer:
            for d in data:
                writer.write(json.dumps(d, ensure_ascii=False) + "\n")

    # 开始处理找到的数据
    print("Filtered %d records for prompt generation." % len(data))
    if len(data) == 0:
        print("No available data found, please check")
        exit(-2)

    class_methods_length_counter = []
    class_fields_length_counter = []
    for instance in data:
        class_methods_length_counter.append(
            len(
                formatter.get_focal_class_other_method(
                    [x.strip() for x in instance[focal_class_other_methods_key]]
                    if focal_class_other_methods_key in instance.keys()
                    else []
                )
            )
        )
        class_fields_length_counter.append(
            len(
                formatter.get_focal_class_field(
                    [x.strip() for x in instance[focal_class_fields_key]]
                    if focal_class_fields_key in instance
                    else parse_fields_from_class_code(instance[focal_class_code_key])
                )
            )
        )
        pass
    # print(np.mean(class_fields_length_counter))
    # print(np.mean(class_methods_length_counter))
    # JSON字符串的格式：
    # {'project':project name
    # 'id': bug_id, e.g., Chart_10
    # 'format': format_strategy,
    # 'prompt':prompt,
    # 'class_signature':className,
    # 'method_signature':methodName}
    #
    for path in tqdm(model_paths):
        # tokenizer = AutoTokenizer.from_pretrained(path)
        model_name = path.split("/")[-1] if path != "chatgpt" else path
        for format in formats[:1]:
            for strategy in strategies[:1]:
                for ignore_feature in ablation_features[:1]:
                    output_file = os.path.join(
                        code_base,
                        "data/prompts/rq1/"
                        + model_name
                        + "_%s_%s_%s.jsonl" % (format, strategy, ignore_feature),
                    )
                    dirname = os.path.dirname(output_file)
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)

                    with open(output_file, "w", encoding="utf-8") as writer:
                        for idx,instance in enumerate(data):
                            if model_name != "chatgpt":
                                is_public = False
                                new_inst = {}
                                bug_id = instance["extra:project_name"]
                                # if bug_id != 'Gson_10_fixed':
                                #     continue
                                new_inst["project"] = bug_id.split("_")[0]
                                new_inst["id"] = bug_id
                                new_inst["strategy"] = strategy
                                new_inst["format"] = format
                                new_inst["ablation"] = ignore_feature
                                new_inst["focal_method"] = instance[focal_method_key]
                                is_public, new_inst["prompt"] = formatter.apply_format(
                                    instance,
                                    model_name,
                                    strategy=strategy,
                                    formatting=format,
                                    ignore_feature=ignore_feature,
                                    project_name=bug_id,
                                )
                                new_inst["class_name"] = bug_id
                                new_inst["method_signature"] = instance[focal_method_signature_key]
                                new_inst["is_public"] = "1" if is_public else "0"
                                writer.write(json.dumps(new_inst, ensure_ascii=False) + "\n")
                            else:
                                new_inst = {}
                                is_public = False
                                bug_id = instance["extra:project_name"]
                                new_inst["id"] = bug_id
                                new_inst["strategy"] = strategy
                                new_inst["format"] = format
                                new_inst["ablation"] = ignore_feature
                                new_inst["focal_method"] = instance[focal_method_key]
                                is_public, new_inst["content"] = formatter.apply_format(
                                    instance,
                                    model_name,
                                    strategy=strategy,
                                    formatting=format,
                                    ignore_feature=ignore_feature,
                                    project_name=bug_id,
                                )
                                new_inst["class_name"] = bug_id
                                new_inst["method_signature"] = instance['source:source_method_signature']
                                new_inst["is_public"] = "1" if is_public else "0"
                                new_inst["role"] = "user"
                                writer.write(json.dumps(new_inst) + "\n")

                    # writer = open(output_file, 'w', encoding='utf-8')
                    # for d in dump_data:
                    #     writer.write(json.dumps(d, ensure_ascii=False) + '\n')
                    # dump_data.clear()
                    # writer.close()
