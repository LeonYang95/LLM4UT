import io
import copy
import chardet
import pickle
from utils.java_parser import parse_import_stmts_from_file_code

imports = ["import org.junit.Test;",
           "import org.junit.Assert;",
           "import org.junit.Before;",
           "import org.junit.After; ",
           "import org.junit.Assert.*;",
           "import org.junit.Ignore;",
           "import org.junit.BeforeClass;",
           "import org.junit.AfterClass;",
           "import org.junit.runner.RunWith;",
           "import org.junit.runners.JUnit4;",
           "import org.junit.Rule;",
           "import org.junit.rules.ExpectedException;",
           "import org.mockito.Mockito.*",
           "import static org.hamcrest.MatcherAssert.assertThat;",
           "import static org.hamcrest.Matchers.*;",
           ]


def add_class_delc(focal_class_path):
    current_imports = imports
    try:
        with open(focal_class_path, 'r', encoding='iso8859-1') as f:
            focal_content = f.read()
        current_imports.extend(parse_import_stmts_from_file_code(focal_content))
    except UnicodeDecodeError as ude:
        with open(focal_class_path, 'rb') as f:
            content = f.read()
            encoding = chardet.detect(content)
        try:
            focal_content = content.decode(encoding=encoding)
            current_imports.extend(parse_import_stmts_from_file_code(focal_content))
        except UnicodeDecodeError as ude:
            pass

    test_class_name = focal_class_path.strip().split('/')[-1].replace('.java', '')
    class_delaration = 'public class ' + test_class_name + '{'

    # 拼接在prompt后面的内容
    res_content = '\n```java\n'
    res_stream = io.StringIO(res_content)

    for imp in current_imports:
        res_stream.write(imp + '\n')
    res_stream.write('\n')
    res_stream.write(class_delaration + '\n')
    return res_stream.getvalue()


def add_class_delc_d4j(src_class_name, src_class_imports: list):
    '''
    project_base: d4j的项目所在的根目录
    project_name: 项目名称， 如 Chart_10
    project_version: fixed/buggy
    focal_class_name: focal class的名称，如 org.jfree.chart.renderer.category.AbstractCategoryItemRenderer  
    '''
    # # 加载对应项目的src和test的路径
    # with open('../utils/test_src.json', 'r') as f:
    #     content_path = json.load(f)
    #
    # focal_class = focal_class_name
    #
    # # 加入focal class的imports
    # if content_path[project_name.lower()]['src'] != '/':
    #     focal_base = content_path[project_name.lower()]['src']
    # else:
    #     focal_base = content_path[project_name.lower()]['src'][1:]
    #
    # focal_base_dir = os.path.join(project_base, project_name, project_version, focal_base)
    # focal_class_file = focal_class.replace('.', '/') + '.java'

    current_imports = pickle.loads(pickle.dumps(imports))
    current_imports.extend(src_class_imports)

    test_class_name = src_class_name.split('.')[-1] + 'Test'
    class_delaration = 'public class ' + test_class_name + '{'

    # 拼接在prompt后面的内容
    res_stream = io.StringIO('')
    res_stream.write('\n```java\n')

    for imp in current_imports:
        res_stream.write(imp + '\n')
    res_stream.write('\n')
    res_stream.write(class_delaration + '\n')
    return res_stream.getvalue()

