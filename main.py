import sys
import argparse
from loguru import logger
from tqdm import *

sys.path.extend([".", ".."])

from configuration import *
from utils.FileUtils import load_jsonl_file
from utils.Common import process_one_output


def evaluate(args):
    # 读取模型输出文件
    if not os.path.exists(args.input_file):
        logger.error(f'Input file {args.input_file} does not exist, please check.')
        exit(-1)
    outputs = load_jsonl_file(args.input_file)
    outputs = [one_output for one_output in outputs if one_output['project'] == args.project]
    logger.info(f'Loaded {len(outputs)} outputs for {args.project} from {args.input_file}')

    # 定义输出文件
    output_base = os.path.dirname(args.output_file)
    if not os.path.exists(output_base):
        logger.warning(f'The directory of expected output file ({output_base}) does not exist, creating one.')
        os.makedirs(output_base)

    for one_output in tqdm(outputs, desc='Evaluating'):
        record = process_one_output(one_output)
    pass


def load_arg_params():
    parser = argparse.ArgumentParser(description='LLM-based unit test generation.')
    parser.add_argument('--project', type=str, help='Target project name, e.g., Chart')
    parser.add_argument("--input-file", type=str,
                        help='Path to the input file. Please refer to README.md for input file formatting.',
                        required=True)
    parser.add_argument('--output-file', type=str, default=f"outputs/default.jsonl",
                        help='Path of the JSONL file to store the generated test classes.', required=True)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = load_arg_params()
    evaluate(args)
