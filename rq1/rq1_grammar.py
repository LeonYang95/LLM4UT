import sys
import os
from tqdm import tqdm

sys.path.extend([".", ".."])

from assistant_methods import run, filter_data_according_to_project
from utils.d4j_utils import load_assistant_data
import configuration
from configuration import output_base_dir, code_base, d4j_proj_base

target_models = configuration.target_models
formats = configuration.formats
strategies = configuration.strategies
ablations = configuration.ablations


def main(target_project="Chart"):
    # 加载辅助数据
    assistant_datas = load_assistant_data()
    # 遍历所有目标模型
    for tgt_model in target_models:
        # 遍历所有prompt格式
        for strategy in strategies:
            # 遍历所有变体
            for ablation in ablations:
                for format in formats:
                    # 定义输出结果的路径
                    output_base = os.path.join(output_base_dir, tgt_model)
                    if not os.path.exists(output_base):
                        os.makedirs(output_base)

                    input_file = os.path.join(
                        code_base,
                        f"data/outputs/{tgt_model}_{format}_{strategy}_{ablation}.jsonl",
                    )

                    if not os.path.exists(input_file):
                        print(
                            "ERROR: Generation file %s does not exist, please check."
                            % input_file
                        )
                        continue
                    if not os.path.exists(d4j_proj_base):
                        print(
                            "ERROR: Defects4j folder %s does not exist, please check"
                            % d4j_proj_base
                        )
                        continue

                    datas = filter_data_according_to_project(
                        input_file, assistant_datas, target_project
                    )

                    print("Load %d generations from %s" % (len(datas), input_file))

                    # 定义输出指标
                    # analyze_res_writer = open(
                    #     f"{output_base}/{target_project}_{format}_{strategy}_{ablation}.jsonl",
                    #     "w",
                    #     encoding="utf-8",
                    # )
                    # 开始遍历模型输出结果，进行编译&测试，统计收集指标
                    for index, data in tqdm(
                            enumerate(datas),
                            total=len(datas),
                            desc=f"Evaluating {tgt_model} on {target_project}",
                    ):
                        if index != 103:
                            continue

                        res_dict = run(
                            model=tgt_model,
                            strategy=strategy,
                            data=data,
                            index=index,
                            ablation=ablation,
                            format=format,
                        )
                    #     analyze_res_writer.write(json.dumps(res_dict) + "\n")
                    # analyze_res_writer.flush()
                    # analyze_res_writer.close()


if __name__ == "__main__":
    proj = sys.argv[1]
    main(proj)

    # from data.configuration import projects
    # for proj in projects:
    #     main(proj)
    #     # break
