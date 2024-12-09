import subprocess
import sys
from collections import Counter

from loguru import logger

sys.path.extend(['.', '..'])
from configuration import *


def check_compile(bug_id, version):
    project_base = os.path.join(d4j_proj_base, f"{bug_id}/{version}")
    if os.path.exists(project_base):
        # 去掉一些影响编译的已有测试用例
        if bug_id.startswith("Lang"):
            if os.path.exists(f"{project_base}/src/test/org/apache/commons/lang/enum"):
                os.system(f"rm -rf {project_base}/src/test/org/apache/commons/lang/enum")
            if os.path.exists(f"{project_base}/src/test/org/apache/commons/lang/AllLangTestSuite.java"):
                os.system(f"rm -f {project_base}/src/test/org/apache/commons/lang/AllLangTestSuite.java")

        if bug_id.startswith('Codec'):
            if os.path.exists(f"{project_base}/src/test/org/apache/commons/codec/language/ColognePhoneticTest.java"):
                # org/apache/commons/codec/language/ColognePhoneticTest.java:113
                os.system(f"rm -rf {project_base}/src/test/org/apache/commons/codec/language/ColognePhoneticTest.java")
            # src/test/org/apache/commons/codec/binary/Base64Test.java
            if os.path.exists(f"{project_base}/src/test/org/apache/commons/codec/binary/Base64Test.java"):
                os.system(f"rm -rf {project_base}/src/test/org/apache/commons/codec/binary/Base64Test.java")

        compilable, err_info, errs = _compile_and_collect_results(project_base)
        return {
            "compilable": compilable,
            "error_msg": err_info,
            "errors": errs,
        }
    else:
        raise FileNotFoundError()


def _compile_and_collect_results(root):
    """
    进行d4j compile过程，并且收集编译结果

    Args:
        root (str): 运行命令的根目录

    Returns:
        compile_flag (str): 表示编译成功，0表示编译失败
        compile_error_msg (str): 编译错误的terminal输出
        compile_error_reasons (Counter): 编译错误的原因

    """
    cur_dir = os.getcwd()
    os.chdir(root)
    compile_error_reasons = Counter()

    # os.environ["LANG"] = "en_US.UTF-8"
    # os.environ["LC_ALL"] = "en_US.UTF-8"

    if 'Codec' in root or 'JacksonDatabind' in root or 'Mockito' in root:
        os.environ['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8'
    else:
        os.environ['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=ISO-8859-1'
    env = os.environ.copy()

    compile_proc = subprocess.run(
        [d4j_command, "compile"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    del os.environ['JAVA_TOOL_OPTIONS']

    os.chdir(cur_dir)

    # extracting error message
    compile_error_lines = compile_proc.stderr.decode("utf-8").split("\n")[2:]
    compile_error_lines = [
        e
        for e in compile_error_lines
        if ("[javac] [" not in e) or ("[exec] [" not in e)
    ]
    compile_error_lines = [
        e for e in compile_error_lines if ("[javac]" in e) or ("[exec]" in e)
    ]
    compile_error_lines = [e for e in compile_error_lines if "warning:" not in e]
    compile_error_lines = [e for e in compile_error_lines if "[javac] Note:" not in e]
    compile_error_lines = [
        e for e in compile_error_lines if "compiler be upgraded." not in e
    ]
    compile_error_msg = "\n".join(compile_error_lines)

    for line in compile_error_lines:
        if "error:" in line:
            start = line.find("error:")
            if start != -1:
                compile_error_reasons[line[start:]] += 1
    compile_flag = True
    if compile_proc.returncode != 0:
        compile_flag = False

    return compile_flag, compile_error_msg, compile_error_reasons


def src_file_by_method_signature(bug_id, version, class_sig):
    if bug_id.lower() in content_path.keys():
        src_path = content_path[bug_id.lower()]['src']
        src_base = os.path.join(d4j_proj_base, bug_id, version, src_path)
        class_path = class_sig.replace('.', os.path.sep)
        file_path = os.path.join(src_base, class_path) + '.java'
        if os.path.exists(file_path):
            return file_path
        else:
            logger.error(f'File {file_path} does not exist, please check')
            return ''
    else:
        logger.error(f'No {bug_id} record found.')
        return ''
    pass
