import os
import json

d4j_home = "/Users/yanglin/Documents/Projects/data/defects4j"
d4j_proj_base = f"{d4j_home}/d4j_projects"
output_dir = "outputs/sample"
code_base = os.path.abspath(os.path.dirname(__file__))
output_base_dir = os.path.join(code_base, output_dir)
d4j_command = f"{d4j_home}/framework/bin/defects4j"
python_bin = "~/anaconda3/envs/codebot/bin/python"

RES_FILE = "/Users/yanglin/Documents/Projects/code-bot/data/outputs/deepseek-coder-6.7b-instruct_comment_extend_full.jsonl"
TMP_FOLDER = "/Users/yanglin/Documents/Projects/code-bot/data/tmp"
GRANULARITY = 'method'
OUTPUT_FILE = '/Users/yanglin/Documents/Projects/example.jsonl'

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
    # "Mockito",
    "JacksonCore",
    "Lang",
    "Jsoup",
    "Chart",
    "Gson",
    "Closure",
    "Codec",
]
with open(os.path.join(code_base, "data/test_src.json"), "r") as f:
    content_path = json.load(f)

pre_defined_imports = [
    "import org.junit.Test;",
    "import org.junit.Assert;",
    "import org.junit.Before;",
    "import org.junit.After;",
    "import static org.junit.Assert.*;",
    "import org.junit.Ignore;",
    "import org.junit.BeforeClass;",
    "import org.junit.AfterClass;",
    "import org.junit.runner.RunWith;",
    "import org.junit.runners.JUnit4;",
    "import org.junit.Rule;",
    "import org.junit.rules.ExpectedException;",
    "import static org.mockito.Mockito.*;",
    "import org.mockito.Mockito;",
]
