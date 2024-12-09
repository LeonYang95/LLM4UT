import pickle
import re
import sys

sys.path.extend(['.', '..'])

from utils.FileUtils import write_test_class
from utils.DependencyUtils import add_dependencies
from utils.JavaAnalyzer import *
from utils.Defects4J import *
from configuration import *


def remove_content_in_parentheses(text):
    """
    去除括号内的内容

    Args:
        text (_type_): 原始的字符串

    Returns:
        str: 去除括号之后的内容
    """
    # This regex pattern finds a pair of parentheses and anything in between.
    pattern = r"\(.*?\)"

    # The re.sub function replaces the pattern with an empty string.
    new_text = re.sub(pattern, "", text)

    return new_text


def analyze_method_signature_for_coverage(method_signature):
    """
    根据待测函数签名，分析收集覆盖率时需要的一些信息，例如类名，包名，函数名，以及变量列表
    Args:
        method_signature: 函数签名

    Returns:
        package_name: 包名
        package_dir: 包名对应的jacoco路径
        class_name: 类名
        class_dir: 类名对应的jacoco路径
        method_name: 函数名
        parameter_tuple: 参数列表
    """
    parameters = re.findall(r"\(.*?\)", method_signature)[0][1:-1]
    parameter_list = [i for i in parameters.split(",") if i != ""]
    tmp_list = []
    for i in parameter_list:
        if "#" in i:
            i = i.replace("#", ".")
        tmp_list.append(i.strip().lower())

    parameter_tuple = tuple(tmp_list)
    package_name = method_signature.split("#")[0]
    class_name = ".".join(method_signature.split("#")[:2])

    ## 测试覆盖率需要的条件
    package_dir = package_name.replace(".", "/")
    clazz_dir = class_name.replace(".", "/")
    method_name = remove_content_in_parentheses(
        "".join(method_signature.split("#")[2:])
    )
    return (
        package_name,
        package_dir,
        class_name,
        clazz_dir,
        method_name,
        parameter_tuple,
    )


def process_one_output(one_output: dict) -> dict:
    one_record = pickle.loads(pickle.dumps(one_output))
    focal_method_signature = one_output['focal_method_signature']
    (package_name, package_dir, class_signature, clazz_dir, method_name,
     parameter_tuple) = analyze_method_signature_for_coverage(focal_method_signature)

    # 提取 completion 中的测试类
    test_class_content = extract_code_blocks(one_output['completion'])

    # 添加/修改 package declaration，将模型生成的测试类单列一个目录，防止对原本的 ut 产生影响
    test_class_content = modify_generated_class(test_class_content)

    # 检查语法正确性
    syntax_correctness = syntax_check(test_class_content)

    if not syntax_correctness:
        # 如果包含语法错误，当前数据处理终止
        one_record['syntax_correct'] = False
        one_record['compliable'] = False
        one_record['pass_execution'] = False
        one_record['covered_lines'] = 0
        one_record['covered_branches'] = 0
        return one_record
    else:
        one_record['syntax_correct'] = True

        # 写文件
        write_test_class(one_record['bug_id'], 'fixed', test_class_content)

        # 添加依赖
        add_dependencies(d4j_proj_base, one_record['bug_id'])

        # 编译
        compile_res = check_compile(one_record['bug_id'], 'fixed')
        one_record['compilable'] = compile_res
        if not compile_res['compilable']:
            # 尝试添加 focal class import 进行修复
            logger.info('Compilation failed, try adding srouce class imports to fix the import issue.')
            src_class_file = src_file_by_method_signature(
                bug_id=one_record['bug_id'],
                version='fixed',
                class_sig=class_signature
            )
            if src_class_file!='':
                with open(src_class_file, 'r', encoding='utf-8') as reader:
                    src_file_content = reader.read()
                imports = parse_imports_from_file(src_file_content)
                new_test_class = add_imports(test_class_content, imports)
                write_test_class(one_record['bug_id'], 'fixed', new_test_class)
                new_compile_res = check_compile(one_record['bug_id'], 'fixed')
            pass

        # 最终能够通过编译且还有测试用例的话，那么执行测试并收集覆盖率

    return one_record


def extract_code_blocks(text) -> str:
    # 使用正则表达式匹配三引号代码块
    pattern = re.compile(r'```([\s\S]*?)```', re.DOTALL)
    code_blocks = pattern.findall(text)

    cleaned_blocks = []
    for block in code_blocks:
        block = block.strip()
        lines = block.split('\n')
        # 判断第一行是否是语言标识（这里用简单方式：如果第一行为纯字母组成则视为语言标识）
        if lines and lines[0].strip().isalpha():
            lines = lines[1:]
        cleaned_block = "\n".join(lines).strip()
        cleaned_blocks.append(cleaned_block)

    return '\n'.join(cleaned_blocks)
