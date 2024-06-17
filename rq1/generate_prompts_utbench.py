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
focal_method_key = "sourceMethodCodeFormat"
focal_class_fields_key = "sourceClassFields"
focal_method_name_key = "sourceMethodName"
focal_method_signature_key = "sourceMethodSignature"
focal_class_other_methods_key = "sourceOtherMethodSignature"
focal_class_constructor_key = "sourceClassConstructors"
focal_class_name_key = "sourceClassName"
focal_class_code_key = "sourceClassCodeFormat"
source_method_paramter_key = "parameterList"
parameter_classes_key = "parameterClassSignatureList"
source_method_signature_key = "sourceMethodSignature"
source_class_imports_key = "sourceClassImports"

if __name__ == "__main__":
    # ablation_idx = int(sys.argv[1])
    ablation_idx = 0
    model_paths = [
        # '/data/public/CodeLlama-7b-hf',
        # '/data/public/CodeLlama-13b-hf',
        # '/data/public/CodeLlama-34b-hf',
        '/data/public/CodeLlama-7b-Instruct-hf',
        '/data/public/CodeLlama-13b-Instruct-hf',
        # '/data/public/CodeLlama-34b-Instruct',
        '/data/public/deepseek-coder-6.7b-instruct',
        # '/data/public/deepseek-coder-33b-instruct',
        # '/data/public/Phind-CodeLlama-34B-v2',
        # '/data/public/starchat-beta',
        # '/data/public/WizardCoder-15B-V1.0',
        # '/data/public/WizardCoder-Python-34B-V1.0'
        # "chatgpt",
        # "Gemma-7b-it"
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
        # "full",
        # 'no_param',
        # 'no_param_constructor',
        # 'no_class_constructor',
        # 'no_class_fields',
        'no_class_other_methods'
    ]
    # ablation_features = [ablation_features[ablation_idx]]

    formatter = PromptFormatter()
    data = []
    input_file = os.path.join(code_base,'data/rq3/UTBenchJava.jsonl')
    with open(input_file,'r',encoding='utf-8') as reader:
        for line in reader.readlines():
            data.append(json.loads(line))

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
        for format in formats:
            for strategy in strategies:
                for ignore_feature in ablation_features:
                    output_file = os.path.join(
                        code_base,
                        "data/prompts/rq3/utbench/"
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
                                bug_id = idx
                                # if bug_id != 'Gson_10_fixed':
                                #     continue
                                new_inst["project"] = instance["projectName"]
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
                                new_inst['prompt'] = new_inst['prompt'].replace('\r','')

                                new_inst["class_name"] = bug_id
                                new_inst["method_signature"] = instance[focal_method_signature_key]
                                new_inst["is_public"] = "1" if is_public else "0"
                                writer.write(json.dumps(new_inst, ensure_ascii=False) + "\n")

                    # writer = open(output_file, 'w', encoding='utf-8')
                    # for d in dump_data:
                    #     writer.write(json.dumps(d, ensure_ascii=False) + '\n')
                    # dump_data.clear()
                    # writer.close()
