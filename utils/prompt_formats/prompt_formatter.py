import sys

sys.path.extend(['.', '..'])

from utils.java_parser import (
    parse_fields_from_class_code,
    parse_param_declaration_from_method_code,
    parse_identifier_in_method_body
)
from utils.output_analyzer import focal_imports, junit_imports
from utils.prompt_formats.extend_postfix import *
import javalang.tree as ast
import javalang.parse as parse
from utils.shell_extractor import extract_test_shell
from utils.d4j_utils import find_test_class

focal_method_key = "source:source_method_code_format"
focal_class_fields_key = "source_class_fields"
focal_method_name_key = 'source:source_method_name'
focal_method_signature_key = 'source:source_method_signature'
focal_class_other_methods_key = "source:source_other_method_signature"
focal_class_constructor_key = "content:source_class_constructors"
focal_class_name_key = "content:source_class_name"
focal_class_code_key = "content:source_class_code_format"
source_method_type_constructor_key = 'content:parameter_class_constructors'
source_method_paramter_key = 'content:parameter_list'
parameter_classes_key = 'content:parameter_class_signature'
source_method_signature_key = 'source:source_method_signature'
source_class_imports_key = 'content:source_class_code_imports'
project_name_key = 'extra:project_name'


# source_method_type_constructor_key = 'parameterClassConstructors'
# focal_method_key = "sourceMethodCodeFormat"
# focal_class_fields_key = "sourceClassFields"
# focal_method_name_key = "sourceMethodName"
# focal_method_signature_key = "sourceMethodSignature"
# focal_class_other_methods_key = "sourceOtherMethodSignature"
# focal_class_constructor_key = "sourceClassConstructors"
# focal_class_name_key = "sourceClassName"
# focal_class_code_key = "sourceClassCodeFormat"
# source_method_paramter_key = "parameterList"
# parameter_classes_key = "parameterClassSignatureList"
# source_method_signature_key = "sourceMethodSignature"
# source_class_imports_key = "sourceClassImports"


class PromptFormatter():

    def __init__(self):
        self.init_prompt = None
        self.generation_post_fix = None

    def base_prompt(self, formatting, focal_method):
        prompt = ''
        if formatting == "natural":
            prompt += "This is the method that you are going to test.\n"
            prompt += "```\n" + focal_method + "\n```\n"
        elif formatting == 'comment':
            prompt += ("```\n"
                       "// The following code is the method that you are going to test.\n")
            prompt += focal_method + '\n'
        return prompt

    def cot_base_prompt(self, focal_method):
        prompt = 'Here is a function written in Java:\n```java\n'
        prompt += "public boolean looksLikeOption(final String trigger) {\n    if (checkForOption != null) {\n        // this is a reentrant call\n        return !checkForOption.equals(trigger);\n    }\n    checkForOption = trigger;\n    try {\n        for (final Iterator i = prefixes.iterator(); i.hasNext(); ) {\n            final String prefix = (String) i.next();\n            if (trigger.startsWith(prefix)) {\n                if (getCurrentOption().canProcess(this, trigger) || getCurrentOption().findOption(trigger) != null) {\n                    return true;\n                }\n            }\n        }\n        return false;\n    } finally {\n        checkForOption = null;\n    }\n}\n"
        prompt += '\n```\n'
        prompt += 'Please finish the following tasks:\n1. Understand the functionality of the function, 2. Summarize its branches, and 3. Give an example as "input-output" pair for each branch.\n'
        prompt += 'Please keep your answer in 200 words.'

    def get_parameters(self, param_names, formatting="natural"):
        '''
        add parameter names into the prompt
        :param param_names: parameter names
        :param formatting: natural or comment
        :return: constructed prompt component
        '''
        if formatting == "natural":
            rt = ''
            if len(param_names) == 1:
                rt += 'The parameter of the method is `%s`.\n' % param_names[0]
                pass
            elif len(param_names) != 0:
                rt += 'There are %d parameters in the method, namely %s.\n' % (
                    len(param_names),
                    ', '.join([
                        '`' + param_str + '`' for param_str in param_names
                    ])
                )
        elif formatting == "comment":
            rt = ''
            if len(param_names) != 0:
                # Parameters
                rt += '\n// The parameter of the method:\n'
                rt += '\n'.join(param_names) + '\n'
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def get_parameter_class_constructors(self, param_class_constructors, formatting="natural"):
        rt = ''
        param_class_constructors = list(set(param_class_constructors))
        if len(param_class_constructors) == 1:
            if '|' in param_class_constructors[0]:
                param_class_constructors = param_class_constructors[0].split('|')
        if formatting == "natural":
            if len(param_class_constructors) != 0:
                if len(param_class_constructors) == 1:
                    rt += "The constructor of the class to which the parameters of the method belong is:`%s`\n" % \
                          param_class_constructors[0]
                else:
                    rt += ("The constructors of the class to which the parameters of the method belong are:\n"
                           "```\n"
                           "%s\n```\n ") % ('\n'.join(param_class_constructors))
        elif formatting == "comment":
            if len(param_class_constructors) != 0:
                rt += "\n// The constructor of the class to which the parameters of the method belong:\n" + '\n'.join(
                    param_class_constructors) + '\n'
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def get_parameter_classes(self, param_classes, formatting="natural"):
        rt = ''
        if formatting == "natural":
            if len(param_classes) != 0:
                if len(param_classes) == 1:
                    rt += 'The parameters come from class `%s`.\n' % param_classes[0]
                else:
                    rt += 'The parameters come from classes : %s.\n' % (
                        ', '.join([
                            '`' + class_sig + '`' for class_sig in param_classes
                        ])
                    )
        elif formatting == "comment":
            if len(param_classes) != 0:
                rt += '\n// The parameters come from:\n' + '\n'.join(param_classes) + '\n'
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def get_focal_class_name(self, focal_class_signature, formatting='natural'):
        prompt = ''
        if formatting == 'natural':
            # Focal Class Constructor
            prompt += "The focal method belongs to the class `%s` .\n" % (focal_class_signature)
            pass
        elif formatting == 'comment':
            prompt += "\n// The method belongs to the class:\n%s\n" % focal_class_signature
            pass
        return prompt

    def get_focal_class_constructor(self, focal_class_constructor, focal_class_signature, formatting="natural"):
        # Focal Class Constructor
        rt = ''
        if formatting == "natural":
            if len(focal_class_constructor) > 1:
                rt += "The focal method belongs to the class `%s`, and the constructors are:\n```\n %s \n```\n" % (
                    focal_class_signature, '\n'.join(focal_class_constructor))
            elif len(focal_class_constructor) == 1:
                rt += "The focal method belongs to the class `%s`, and the constructor is `%s`\n" % (
                    focal_class_signature, '\n'.join(focal_class_constructor))
        elif formatting == "comment":
            rt += "\n// The method belongs to the class:\n%s\n" % focal_class_signature
            # Focal Class Constructor
            if len(focal_class_constructor) != 0:
                rt += '\n// Constructor:\n'
                rt += '\n'.join(focal_class_constructor) + '\n'
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def get_focal_class_field(self, focal_class_fields, formatting="natural"):
        rt = ''
        if formatting == "natural":
            if len(focal_class_fields) != 0:
                if isinstance(focal_class_fields[0], dict):
                    focal_class_fields = [x['declaration_text'] for x in focal_class_fields]
                if len(focal_class_fields) == 1:
                    rt += 'This is the field defined in the class: `%s`.\n' % (
                        '\n'.join(focal_class_fields))
                    pass
                else:
                    rt += "These are the fields defined in the class:\n```\n%s\n```\n" % (
                        '\n'.join(focal_class_fields))
                    pass
        elif formatting == "comment":
            # Focal class fields
            if len(focal_class_fields) != 0:
                rt += '\n// Fields\n'
                if isinstance(focal_class_fields[0], dict):
                    focal_class_fields = [x['declaration_text'] for x in focal_class_fields]
                rt += '\n'.join(focal_class_fields) + '\n'
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def get_focal_class_other_method(self, focal_class_other_methods, formatting="natural"):
        rt = ''
        if formatting == "natural":
            if len(focal_class_other_methods) != 0:
                if len(focal_class_other_methods) == 1:
                    rt += 'This is the method defined in the class: `%s`\n' % focal_class_other_methods[
                        0].strip()
                    pass
                else:
                    rt += "These are the methods defined in the class :\n```\n%s\n```\n" % (
                        '\n'.join(focal_class_other_methods))
        elif formatting == "comment":
            # Focal Class other methods
            if len(focal_class_other_methods) != 0:
                rt += '\n// Other methods\n'
                rt += '\n'.join(focal_class_other_methods)
        else:
            raise NotImplementedError("UNKNOWN FORMATTING.")
        return rt

    def is_method_public(self, java_code):
        # Parse the Java code
        java_code = 'class Test {\n' + java_code.replace('\r\n', '\n\n') + '\n}'
        tree = parse.parse(java_code)

        # Search for the method
        for path, node in tree.filter(ast.MethodDeclaration):
            if node:
                for modifier in node.modifiers:
                    if modifier == 'public':
                        return True
                    elif modifier in ['private', 'protected']:
                        return False
        return False
        # raise ValueError(f"No method found with the name '{method_name}'")

    def apply_format(self, data, model_name, strategy='generation', formatting="natural", ignore_feature="constructed",
                     project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)

        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        elif 'gemma' in model_name.lower():
            BasicModel = Gemma

        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += self.base_prompt(formatting, focal_method)

        if ignore_feature != 'no_param':
            prompt += self.get_parameters(parameters, formatting)
            prompt += self.get_parameter_classes(parameter_classes, formatting)
            pass

        if ignore_feature != 'no_param_constructor' and ignore_feature != 'no_param':
            prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)
            pass

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        # if ignore_feature == "constructed":
        #     prompt = self.get_constructed_prompt(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_class":
        #     prompt = self.get_ablation_prompt_no_class_fields(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_param":
        #     prompt = self.get_ablation_prompt_no_param(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_param_constructor":
        #     prompt = self.get_ablation_prompt_no_param_constructor(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_class_constructor":
        #     prompt = self.get_ablation_prompt_no_class_constructor(data, formatting=formatting, strategy=strategy)

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_remove_redundant_info(self, data, model_name, strategy='generation', formatting="natural",
                                           ignore_feature="constructed",
                                           project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)
        used_identifiers = parse_identifier_in_method_body(focal_method)
        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)

        if len(focal_class_fields) != 0:
            used_fields = []
            for field in focal_class_fields:
                if field['field_name'] in used_identifiers:
                    used_fields.append(field)
            focal_class_fields = pickle.loads(pickle.dumps(used_fields))

        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []

        if len(focal_class_other_methods) != 0:
            used_focal_other_methods = []
            for focal_class_method in focal_class_other_methods:
                decl_lines = focal_class_method.split('\n')
                decl_line = ''
                if len(decl_lines) > 1:
                    for cur_line in decl_lines:
                        if cur_line.startswith('@'):
                            continue
                        else:
                            decl_line = cur_line
                            break
                    pass
                else:
                    decl_line = decl_lines[0]
                method_name = decl_line.split('(')[0].split(' ')[-1]
                if method_name in used_identifiers:
                    used_focal_other_methods.append(focal_class_method)
                pass
            focal_class_other_methods = pickle.loads(pickle.dumps(used_focal_other_methods))

        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        elif 'gemma' in model_name.lower():
            BasicModel = Gemma

        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += self.base_prompt(formatting, focal_method)

        if ignore_feature != 'no_param':
            prompt += self.get_parameters(parameters, formatting)
            prompt += self.get_parameter_classes(parameter_classes, formatting)
            pass

        if ignore_feature != 'no_param_constructor' and ignore_feature != 'no_param':
            prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)
            pass

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        # if ignore_feature == "constructed":
        #     prompt = self.get_constructed_prompt(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_class":
        #     prompt = self.get_ablation_prompt_no_class_fields(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_param":
        #     prompt = self.get_ablation_prompt_no_param(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_param_constructor":
        #     prompt = self.get_ablation_prompt_no_param_constructor(data, formatting=formatting, strategy=strategy)
        # elif ignore_feature == "no_class_constructor":
        #     prompt = self.get_ablation_prompt_no_class_constructor(data, formatting=formatting, strategy=strategy)

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_CoT_first_round(self, data, model_name):
        focal_method = data[focal_method_key]
        if 'deepseek' in model_name.lower():
            BasicModel = DeepSeek_Coder_Chat()
        elif 'phind' in model_name.lower():
            BasicModel = Phind_Chat()
        elif 'codellama' in model_name.lower():
            BasicModel = CodeLlama_Chat()
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        elif 'gemma' in model_name.lower():
            BasicModel = Gemma

        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        conversations = []
        conversations.append({
            'role': 'system',
            'message': 'Your task is to write unit tests to check the correctness of a method.'
        })
        conversations.append({
            'role': 'init_user',
            'message': "Here is a method written in Java: \n```java\n public boolean looksLikeOption(final String trigger) {\n    if (checkForOption != null) {\n        // this is a reentrant call\n        return !checkForOption.equals(trigger);\n    }\n    checkForOption = trigger;\n    try {\n        for (final Iterator i = prefixes.iterator(); i.hasNext(); ) {\n            final String prefix = (String) i.next();\n            if (trigger.startsWith(prefix)) {\n                if (getCurrentOption().canProcess(this, trigger) || getCurrentOption().findOption(trigger) != null) {\n                    return true;\n                }\n            }\n        }\n        return false;\n    } finally {\n        checkForOption = null;\n    }\n}\n```\n"
                       "Please do the following:\n"
                       "1. Understand its functionality,\n"
                       "2. Summarize its branches and \n"
                       "3. give an example of input-output expectation for each branch. \n"
                       "Please keep your answer in 200 words."
        })
        conversations.append({
            'role': "init_response",
            'message': "This Java method, looksLikeOption, checks if a given string (trigger) resembles an option based on certain prefixes and conditions:\n"
                       "\n1. Functionality: The method iterates over a collection of prefixes. If trigger starts with any of these prefixes and either getCurrentOption().canProcess(this, trigger) returns true or getCurrentOption().findOption(trigger) is not null, the method returns true. Otherwise, it returns false.\n"
                       "2. Branches:\n"
                       "   - Branch 1: checkForOption != null - This is a reentrant call, and the function returns the negation of the comparison between checkForOption and trigger.\n"
                       "   - Branch 2: trigger.startsWith(prefix) - If trigger starts with a prefix.\n"
                       "   - Branch 3: getCurrentOption().canProcess(this, trigger) or getCurrentOption().findOption(trigger) != null - If the current option can process the trigger or finds an option for the trigger.\n"
                       "\n3. Input-Output Expectations:\n"
                       "   - Branch 1: Input: trigger = \"option1\", checkForOption = \"option2\"; Output: true\n"
                       "   - Branch 2: Input: trigger = \"opt1\", prefixes = [\"opt\", \"cmd\"]; Output: Depends on the result of getCurrentOption() methods.\n"
                       "   - Branch 3: Input: trigger = \"opt1\", getCurrentOption().canProcess(this, \"opt1\") = true; Output: true\n"
                       "\nThe actual output for Branch 2 and Branch 3 would depend on the implementation of getCurrentOption() and its methods.\n"
        })

        conversations.append({
            "role": 'user',
            "message": f"Here is a method written in Java: \n```java\n {focal_method} \n```\n"
                       "Please do the following:\n"
                       "1. Understand its functionality,\n"
                       "2. Summarize its branches and \n"
                       "3. give an example of input-output expectation for each branch. \n"
                       "Please keep your answer in 200 words."
        })
        conversations.append({
            "role": 'assistant',
            "message": None
        })

        prompt = BasicModel.apply_chat(conversations)
        return self.is_method_public(focal_method), prompt

    def apply_format_focal_at_end(self, data, model_name, strategy='generation', formatting="natural",
                                  ignore_feature="constructed",
                                  project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        # prompt += '\n```\n'
        prompt += "Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.\n```\n"

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        prompt += "\n// The following code is the method that you are going to test.\n"
        prompt += focal_method + '\n'
        prompt += self.get_parameters(parameters, formatting)
        prompt += self.get_parameter_classes(parameter_classes, formatting)
        prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)

        if formatting == 'comment':
            prompt += '\n```\n'

        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_AutoCoT(self, data, model_name, strategy='extend', formatting="comment",
                             ignore_feature="full",
                             project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += "Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction.\n```\n"

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        prompt += "\n// The following code is the method that you are going to test.\n"
        prompt += focal_method + '\n'
        prompt += self.get_parameters(parameters, formatting)
        prompt += self.get_parameter_classes(parameter_classes, formatting)
        prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)

        if formatting == 'comment':
            prompt += '\n```\n'

        prompt += BasicModel.autoCoT_postfix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_focal_at_end_improve_instruction(self, data, model_name, strategy='generation',
                                                      formatting="natural",
                                                      ignore_feature="constructed",
                                                      project_name=""):
        def _parse_header(method_code:str):
            tree = parse.parse(f"class Test {{\n{method_code}\n}}")
            for path, node in tree.filter(ast.MethodDeclaration):
                return node.modifiers
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_method_name = data[focal_method_name_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []




        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        # prompt += '\n```\n'
        prompt += "Your Task is to write some unit tests, and the method you are going to test is at the end of the instruction. Followed by a few instruction on generating high quality unit tests.\n```\n"

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        prompt += "\n// The following code is the method that you are going to test.\n"
        prompt += focal_method + '\n'
        prompt += self.get_parameters(parameters, formatting)
        prompt += self.get_parameter_classes(parameter_classes, formatting)
        prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)

        if formatting == 'comment':
            prompt += '\n```\n'

        prompt += (
            f"Please first analyze the branches of the source method `{data[focal_method_name_key]}`.\n Then write some unit tests to cover these branches. "
            f"Please make sure that the unit tests cover as many branches of method `{focal_method_name}` as possible, and you can flexibly use Mocks and perform appropriate initialization as neede for testsing. ")
        if 'content:callee_signature' in data.keys() and len(data['content:callee_signature']) != 0:
            callee_names = [''.join(x.split('(')[:-1]).split('#')[-1] for x in data['content:callee_signature']]
            prompt += " For example, you can selectively handle the following method invocation using Mockito framework: " + ', '.join(
                callee_names) + ". "
        header = _parse_header(focal_method)
        if 'static' in header:
            focal_method_invocation = f"\nYou need to use `{focal_class_name}.{focal_method_name}` to invoke the method `{focal_method_name}`."
        else:
            focal_method_invocation = f"\nYou need to first create an object instance of the class `{focal_class_name}`, such as `{focal_class_name.lower()}`, and then use `{focal_class_name.lower()}.{focal_method_name}` to invoke the method `{focal_method_name}`."
        prompt += (
            f"{focal_method_invocation}\n"
            f"You also need to pay attention to distinguishing the scope modifiers to avoid directly calling `private/protected` methods and to avoid incorrectly calling `static` methods. \n"
            f"Please wrap the unit tests in one class.\n")

        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_focal_between_fields_and_other_methods(self, data, model_name, strategy='generation',
                                                            formatting="natural",
                                                            ignore_feature="constructed",
                                                            project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt
        prompt += "Your Task is to write some unit tests, and the method you are going to test is listed between the class fireds and class other methods in the instuction.\n```\n"
        # prompt += '\n```\n'
        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass

        prompt += "\n// The following code is the method that you are going to test.\n"
        prompt += focal_method + '\n'
        prompt += self.get_parameters(parameters, formatting)
        prompt += self.get_parameter_classes(parameter_classes, formatting)
        prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)

        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_focal_after_constructor(self, data, model_name, strategy='generation', formatting="natural",
                                             ignore_feature="constructed",
                                             project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt
        prompt += "Your Task is to write some unit tests, and the method you are going to test is listed after the constructor of the class it bleongs.\n```\n"
        prompt += '\n```\n'
        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        prompt += "\n// The following code is the method that you are going to test.\n"
        prompt += focal_method + '\n'
        prompt += self.get_parameters(parameters, formatting)
        prompt += self.get_parameter_classes(parameter_classes, formatting)
        prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass

        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_with_shell(self, data, model_name, strategy='generation', formatting="natural",
                                ignore_feature="constructed",
                                project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        elif 'gemma' in model_name.lower():
            BasicModel = Gemma
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += self.base_prompt(formatting, focal_method)

        if ignore_feature != 'no_param':
            prompt += self.get_parameters(parameters, formatting)
            prompt += self.get_parameter_classes(parameter_classes, formatting)
            pass

        if ignore_feature != 'no_param_constructor' and ignore_feature != 'no_param':
            prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)
            pass

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = '\n```java\n' + data['test_shell']
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_switch_fields_and_other_methods(self, data, model_name, strategy='generation',
                                                     formatting="natural", ignore_feature="constructed",
                                                     project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        elif 'gemma' in model_name.lower():
            BasicModel = Gemma

        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += self.base_prompt(formatting, focal_method)

        if ignore_feature != 'no_param':
            prompt += self.get_parameters(parameters, formatting)
            prompt += self.get_parameter_classes(parameter_classes, formatting)
            pass

        if ignore_feature != 'no_param_constructor' and ignore_feature != 'no_param':
            prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)
            pass

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        prompt += '\n'

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass

        if formatting == 'comment':
            prompt += '\n```\n'
        prompt += BasicModel.generation_post_fix
        if strategy == "extend":
            extend_postfix = add_class_delc_d4j(focal_class_signature, focal_class_imports)
            prompt += extend_postfix

        return self.is_method_public(focal_method), prompt

    def apply_format_shell_in_prompt_Eval(self, data, model_name,
                                          strategy='generation', formatting="comment",
                                          ignore_feature="constructed",
                                          project_name=""):
        focal_method = data[focal_method_key]
        focal_class_name = data[focal_class_name_key]
        focal_class = data[focal_class_code_key]
        focal_method_signature = data[focal_method_signature_key]
        focal_class_signature = '.'.join(focal_method_signature.split('#')[:2])
        focal_class_imports = data[source_class_imports_key]

        param_dict = parse_param_declaration_from_method_code(focal_method)
        # parameters = data[source_method_paramter_key]
        parameters = [k for k, v in param_dict.items()]
        param_types = [v for k, v in param_dict.items()]
        collected_parameter_classes = list(set([
            item.split('|')[0].replace('#', '.') for item in data[parameter_classes_key]
        ]))
        parameter_classes = []
        if len(collected_parameter_classes) == 0 and len(param_types) != 0:
            parameter_classes = pickle.loads(pickle.dumps(param_types))
        elif len(collected_parameter_classes) != 0:
            assert len(param_types) != 0
            for type in param_types:
                found = False
                for class_sig in collected_parameter_classes:
                    class_sig = class_sig.strip()
                    if class_sig.endswith('.' + type):
                        parameter_classes.append(class_sig)
                        found = True
                        break
                if not found:
                    parameter_classes.append(type)

        focal_class_fields = [x.strip() for x in data[
            focal_class_fields_key]] if focal_class_fields_key in data.keys() else parse_fields_from_class_code(
            focal_class)
        focal_class_other_methods = [x.strip() for x in data[
            focal_class_other_methods_key]] if focal_class_other_methods_key in data.keys() else []
        focal_class_constructor = [x.strip() for x in
                                   data[
                                       focal_class_constructor_key]] if focal_class_constructor_key in data.keys() else ""

        source_method_parameter_class_constructors = [x.strip() for x in data[
            source_method_type_constructor_key]] if source_method_type_constructor_key in data.keys() else []

        BasicModel = None
        if 'deepseek' in model_name.lower():
            BasicModel = Deepseek
        elif 'phind' in model_name.lower():
            BasicModel = Phind
        elif 'codellama' in model_name.lower():
            BasicModel = Codellama
        elif 'starchat' in model_name.lower():
            BasicModel = Starchat
        elif 'wizardcoder' in model_name.lower():
            BasicModel = Wizardcoder
        elif 'chatgpt' in model_name.lower():
            BasicModel = ChatGPT
        else:
            raise NotImplementedError("The model %s is not implemented yet, please check." % model_name)

        prompt = BasicModel.init_prompt

        prompt += self.base_prompt(formatting, focal_method)

        if ignore_feature != 'no_param':
            prompt += self.get_parameters(parameters, formatting)
            prompt += self.get_parameter_classes(parameter_classes, formatting)
            pass

        if ignore_feature != 'no_param_constructor' and ignore_feature != 'no_param':
            prompt += self.get_parameter_class_constructors(source_method_parameter_class_constructors, formatting)
            pass

        # 这里如果不需要constructor，需要把class name拿出来
        if ignore_feature != 'no_class_constructor':
            prompt += self.get_focal_class_constructor(focal_class_constructor, focal_class_signature, formatting)
            pass
        else:
            prompt += self.get_focal_class_name(focal_class_signature, formatting)

        if ignore_feature != 'no_class_fields':
            prompt += self.get_focal_class_field(focal_class_fields, formatting)
            pass
        if ignore_feature != 'no_class_other_methods':
            prompt += self.get_focal_class_other_method(focal_class_other_methods, formatting)
            pass

        prompt += "\n\n// Given the Following test class:\n"

        bug_id = '_'.join(data[project_name_key].split('_')[:2])
        focal_class_sig = '.'.join(data[source_method_signature_key].split('#')[:2])
        src_file, test_file = find_test_class(bug_id, focal_class_sig)
        is_junit3 = False
        if test_file:
            with open(test_file, 'r', encoding='utf-8') as reader:
                test_class_code = reader.read()
                imports = parse_import_stmts_from_file_code(test_class_code)
                for imp in imports:
                    if 'junit.framework' in imp:
                        is_junit3 = True
                        break
                prompt += extract_test_shell(test_class_code, data[focal_class_name_key]) + '\n```\n'
            pass
        else:
            # imports from focal class
            if len(focal_class_imports) != 0:
                prompt += '\n'.join(focal_class_imports) + '\n'
                prompt += '\n'.join(junit_imports) + '\n'
            # imports from pre-defined imports
            else:
                prompt += '\n'.join(focal_imports)
            prompt += 'import {}'.format('.'.join(focal_class_signature.split('.')[:-1]) + '.*;\n')
            prompt += f'public class {focal_class_name}Tests {{\n\t\n}}\n```\n'
            pass

        prompt += BasicModel.generation_post_fix.format(3 if is_junit3 else 4)
        return self.is_method_public(focal_method), prompt


from abc import abstractmethod


class BasicModel():
    @abstractmethod
    def apply_chat(self, conversation):
        pass


class Deepseek():
    init_prompt = "You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.\n" + '### Instruction:\n'
    generation_post_fix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.\n### Response:"
    autoCoT_postfix = "Your task is to write unit tests in Java 1.7 and Junit 4 with maximizing both branch and line coverage. Let’s first understand the problem and devise a plan to solve the problem. Then, let’s carry out the plan and solve the problem step by step.\n### Response:"


class Codellama():
    init_prompt = "[INST] Your task is to write unit tests to check the correctness of a method.\n"
    generation_post_fix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage. Please ensure that the output format is in Markdown. [/INST] "
    autoCoT_postfix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage. Let’s first understand the problem and devise a plan to solve the problem. Then, let’s carry out the plan and solve the problem step by step. Please ensure that the output format is in Markdown. [/INST] "


class Phind():
    init_prompt = "### System Prompt\nYou are an intelligent programming assistant.\n\n" + '### User Message:\n'
    generation_post_fix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.\n\n### Assistant:"
    autoCoT_postfix = "Your task is to write unit tests in Java 1.7 and Junit 4 with maximizing both branch and line coverage. Let’s first understand the problem and devise a plan to solve the problem. Then, let’s carry out the plan and solve the problem step by step.\n### Assistant:"


class Starchat():
    init_prompt = "<|system|>\nYou are an intelligent programming assistant.<|end|>\n<|user|>\n"
    generation_post_fix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.<|end|>\n<|assistant|>"


class Wizardcoder():
    init_prompt = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n" + '### Instruction:\n'
    generation_post_fix = "Please write some unit tests in Java 1.7 and JUnit 4 with maximizing both branch and line coverage.\n\n### Response:"


class ChatGPT():
    init_prompt = 'You are a professional who writes Java test methods. Please help me write some unit tests in java language, details are listed below: \n\n.'
    generation_post_fix = "Please write some unit tests in Java 1.7 and Junit 4 with maximizing both branch and line coverage. Please ensure that the output format is Markdown, and no explainations needed."


class Gemma():
    init_prompt = '<start_of_turn>user\n'
    generation_post_fix = 'Please write some unit tests in Java 1.7 and Junit 4 with maximizing both branch and line coverage. Please ensure that the output format is Markdown, and no explainations needed.<end_of_turn>\n<start_of_turn>model'


class CodeLlama_Chat(BasicModel):

    def apply_chat(self, conversations):
        prompt = ""
        for conversation in conversations:
            role = conversation['role']
            message = conversation['message']
            if role == 'system':
                # Your task is to write unit tests to check the correctness of a method.
                prompt += f"<s>[INST] <<SYS>>\n{message}\n<</SYS>>\n\n"
            if role == 'init_user':
                prompt += f"{message} [/INST] "
            if role == 'init_response':
                prompt += f"{message} </s>"
            if role == "user":
                prompt += f"<s>[INST] {message} [/INST] "
            if role == 'assistant':
                if message:
                    prompt += f" {message} </s>"
                else:
                    pass

        return prompt


class DeepSeek_Coder_Chat(BasicModel):

    def apply_chat(self, conversations):
        prompt = ""
        for conversation in conversations:
            role = conversation['role']
            message = conversation['message']
            if role == 'system':
                prompt += "You are an AI programming assistant, utilizing the DeepSeek Coder model, developed by DeepSeek Company, and you only answer questions related to computer science. For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer.\n"
            if role in ["user", "init_user"]:
                prompt += f"### Instruction:\n {message} \n"
            if role in ['assistant', 'init_response']:
                if message:
                    prompt += f"### Response:\n {message} <|EOT|>\n"
                else:
                    prompt += f"### Response:"

        return prompt


class Phind_Chat(BasicModel):

    def apply_chat(self, conversations):
        prompt = ""
        for conversation in conversations:
            role = conversation['role']
            message = conversation['message']
            if role == 'system':
                prompt += "### System Prompt\nYou are an intelligent programming assistant.\n\n"
            if role in ["user", 'init_user']:
                prompt += f"### User Message:\n {message} \n\n"
            if role in ['assistant', 'init_response']:
                if message:
                    prompt += f"### Assistant:\n {message} \n\n"
                else:
                    prompt += f"### Assistant:"
        return prompt

#
