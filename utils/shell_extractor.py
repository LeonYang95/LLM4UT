import sys

sys.path.extend(['.', '..'])

from utils.java_parser import (
    parse_methods_from_class_node,
    parse_fields_from_class_code,
    parse_classes_from_file_node,
    parse_superclass_or_interface_from_class_node,
    parse_import_stmts_from_file_code
)


def extract_test_shell(class_str, class_name):
    imports = parse_import_stmts_from_file_code(class_str)
    methods = parse_methods_from_class_node(class_str, need_prefix=False)
    fields = parse_fields_from_class_code(class_str, need_prefix=False)
    inner_classes = parse_classes_from_file_node(class_str)
    extend_classes = parse_superclass_or_interface_from_class_node(class_str)
    test_shell = ''
    is_junit3 = False
    removed_methods = []

    for imp in imports:
        if 'junit.framework' in imp:
            is_junit3 = True
        test_shell += imp + '\n'
    test_shell += f"public class {class_name} "
    if len(extend_classes['superclasses']) != 0:
        test_shell += ' '.join(extend_classes['superclasses'])
    if len(extend_classes['interfaces']) != 0:
        test_shell += f" implements {' '.join(extend_classes['interfaces'])}"
    test_shell += "{\n"
    test_shell += "\t" + "\n\t".join([field['declaration_text'] for field in fields])
    test_shell += "\n"
    removed_method_range = []
    for method in methods:
        if is_junit3:
            if method['method_name'].startswith('test'):
                removed_methods.append([method['method_start_line'], method['method_end_line']])
                continue
            else:
                if any([method['method_start_line'] in range(removed_line[0], removed_line[1]) for removed_line in
                        removed_methods]):
                    continue
        else:
            if '@Test' in method['method_modifiers']:
                removed_method_range.append([method['method_start_line'], method['method_end_line']])
                continue

            else:
                if any([method['method_start_line'] in range(removed_lines[0], removed_lines[1])
                        for removed_lines in removed_method_range]):
                    continue

        test_shell += "\n\t" + method['method_text']
    test_shell += '}\n'
    for inner_class in inner_classes:
        test_shell += inner_class + '\n'

    return test_shell


if __name__ == '__main__':
    class_str = 'import java.utils.String; \n public class SomeTests extends TestCase{ private int testFields = 0; @Test public void test1(){ int i = 1; i+=1; } @Before public void test2(){ int i = 0; i+=1; } } class InnerClass{ SomeType someVariavle;}'
    extract_test_shell(class_str, 'SomeTests')
    pass
