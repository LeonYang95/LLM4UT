import os 
from tree_sitter import Language
d4j_home = "/path/to/defects4j"
d4j_proj_base = f"{d4j_home}/d4j_projects"
output_dir = 'data/rq1/results_1220'
code_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
output_base_dir = os.path.join(code_base, output_dir)
python_bin = '/path/to/your/python/enivronment/bin/python'
dej_command = f'{d4j_home}/framework/bin/defects4j'
Language.build_library(
    os.path.join(code_base, "data/build/java.so"),
    [os.path.join(code_base, "data/tree-sitter-java")],
)
JAVA_LANGUAGE = Language(os.path.join(code_base,'data/build/java.so'), 'java')

# proxy_host = "None"
# proxy_port = "None"
# proxy_username = "None"
# proxy_password = "None"

proxy_host = None
proxy_port = None
proxy_username = None
proxy_password = None

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
    "Mockito",
    "JacksonCore",
    "Lang",
    "Jsoup",
    "Chart",
    "Gson",
    "Closure",
    "Codec"
]

target_models = [
    # "WizardCoder-Python-34B-V1.0",
    # "CodeLlama-7b-hf",
    "CodeLlama-7b-Instruct-hf",
    # "CodeLlama-13b-hf",
    "CodeLlama-13b-Instruct-hf",
    # "CodeLlama-34b-hf",
    # "CodeLlama-34b-Instruct",
    "deepseek-coder-6.7b-instruct",
    "deepseek-coder-33b-instruct",
    "Phind-CodeLlama-34B-v2",
    # "starchat-beta",
    # "WizardCoder-15B-V1.0"，

]

formats = [
    'comment',
    # 'natural'
]

strategies = [
    'generation',
    # 'extend'
]

ablations = [
    'full',
    'no_param',
    'no_param_constructor',
    'no_class_constructor',
    'no_class_fields',
    'no_class_other_methods'
]