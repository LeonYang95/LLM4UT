from collections import defaultdict
import xml.etree.ElementTree as ET
import re


def to_jave_bytecode_types(c_str: str):
    # ["B", "C", "D", "F", "I", "J", "Z", "S"]
    if c_str == "B":
        return "java.lang.byte"
    elif c_str == "C":
        return "java.lang.character"
    elif c_str == "D":
        return "java.lang.double"
    elif c_str == "F":
        return "java.lang.float"
    elif c_str == "I":
        return "java.lang.integer"
    elif c_str == "J":
        return "java.lang.long"
    elif c_str == "Z":
        return "java.lang.boolean"
    elif c_str == "S":
        return "java.lang.short"
    elif c_str.startswith("L"):
        return c_str[1:].replace("/", ".")
    elif c_str.startswith("["):
        return to_jave_bytecode_types(c_str[1:]) + "[]"
    else:
        raise NotImplementedError("class type %s not implemented yet" % c_str)


def parse_coverage_xml(coverage_report):
    """
    Load and parse the JaCoCo XML coverage report

    Args:
        coverage_report (str): jacoco生成的覆盖率报告路径

    Raises:
        NotImplementedError: 不支持的变量类型，请联系开发人员

    Returns:
        dict: 经过分析之后的jacoco覆盖率指标
    """
    tree = ET.parse(coverage_report)
    root = tree.getroot()

    coverage_data = defaultdict()
    # Iterate over the packages in the XML and collect data
    for package in root.findall(".//package"):
        package_name = package.attrib["name"]
        coverage_data[package_name] = defaultdict()

        for clazz in package.findall(".//class"):
            clazz_name = clazz.attrib["name"]
            if clazz.findall(".//method"):
                coverage_data[package_name][clazz_name] = defaultdict()

                for method in clazz.findall(".//method"):
                    method_name = method.attrib["name"]
                    pattern = r"\(.*?\)"
                    # parameters =  method.attrib["signature"]
                    parameters = re.findall(pattern, method.attrib["signature"])[0][1:-1]
                    raw_param_list = parameters.split(";")
                    parameter_list = []

                    for param_str in raw_param_list:
                        if param_str == "":
                            continue
                        else:
                            param_stack = []

                            for i in range(len(param_str)):
                                c_str = param_str[i]
                                if c_str == "[":
                                    param_stack.append(c_str)
                                    continue
                                elif c_str == "L":
                                    param_stack.append(param_str[i:])
                                    res = "".join(param_stack)
                                    parameter_list.append(
                                        to_jave_bytecode_types(res).lower()
                                    )
                                    param_stack.clear()
                                    break
                                elif c_str in ["B", "C", "D", "F", "I", "J", "Z", "S"]:
                                    param_stack.append(c_str)
                                    pass
                                else:
                                    raise NotImplementedError(
                                        "Class Type %s not implemented yet." % c_str
                                    )
                                res = "".join(param_stack)
                                parameter_list.append(
                                    to_jave_bytecode_types(res).lower()
                                )
                                param_stack.clear()

                    tmp_list = []
                    for i in parameter_list:
                        if "/" in i:
                            tmp_list.append(i.split("/")[-1])
                        else:
                            tmp_list.append(i)
                    parameter_tuple = tuple(tmp_list)

                    if method_name not in coverage_data[package_name][clazz_name]:
                        coverage_data[package_name][clazz_name][
                            method_name
                        ] = defaultdict()
                    coverage_data[package_name][clazz_name][method_name][
                        parameter_tuple
                    ] = defaultdict()
                    
                    total_lines = 0
                    covered_lines = 0
                                        
                    total_branches = 0
                    covered_branches = 0
                    
                    for single_line in method.findall(".//line"):
                        if int(single_line.attrib["hits"]) > 0:
                            covered_lines += 1
                        total_lines += 1

                        if "condition-coverage" in single_line.attrib:
                            branch_nums = re.findall(pattern, single_line.attrib["condition-coverage"])[0][1:-1]
                            covered_branches += int(branch_nums.split("/")[0])
                            total_branches += int(branch_nums.split("/")[1])
                    
                    if total_lines != 0:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["line_coverage"] = {
                            "covered_lines": covered_lines,
                            "missed_lines": total_lines - covered_lines,
                        }
                    else:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["line_coverage"] = None

                
                    if total_branches != 0:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["branch_coverage"] = {
                            "covered_branches": covered_branches,
                            "missed_branches": total_branches - covered_branches,
                        }
                    else:
                        coverage_data[package_name][clazz_name][method_name][
                            parameter_tuple
                        ]["branch_coverage"] = None
    return coverage_data


