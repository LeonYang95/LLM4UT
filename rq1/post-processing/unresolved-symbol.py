import sys

# Extend the system path to include the current and parent directory
sys.path.extend(['.', '..'])
import os
import json
import re
import pickle
from configuration import output_base_dir, target_models, projects


def filter_affect_records_by_unresolved_symbol_type(record_file, target_type):
    """
    This function filters the records by unresolved symbol type.

    Parameters:
    record_file (str): The path to the record file.
    target_type (str): The target type of unresolved symbol.

    Returns:
    list: A list of records that match the target unresolved symbol type.
    """
    ret = []
    with open(record_file, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            instance = json.loads(line.strip())
            if instance['first_compile_error'] != '':
                err_lines = instance['first_compile_error'].split('\n')
                total_errors = get_all_compile_errors(instance['first_compile_error'])
                matched_unresolved_errors = 0
                for index, line in enumerate(err_lines):
                    res = re.findall(r"symbol:[ ]+(\w+) (\w+)", line)
                    if res:
                        for type, identifier in res:
                            if type == target_type:
                                matched_unresolved_errors += 1

                if total_errors == matched_unresolved_errors:
                    ret.append(pickle.loads(pickle.dumps(instance)))
    return ret


def get_all_compile_errors(err_msg):
    """
    This function gets all compile errors from the error message.

    Parameters:
    err_msg (str): The error message.

    Returns:
    int: The number of compile errors. If no errors are found, the function returns None.
    """
    res = re.findall(r'\[javac\] (\d+) errors', err_msg)
    if res:
        return int(res[0])
    pass


if __name__ == '__main__':
    # For each model in target models, filter the records by unresolved symbol type 'class'
    for model in target_models:
        records = []
        for project in projects:
            record_file = f"{project}_comment_extend_full.jsonl"
            record_file = os.path.join(output_base_dir, f"{model}/{record_file}")
            records.extend(filter_affect_records_by_unresolved_symbol_type(record_file, 'variable'))
            print()
        print(len(records))
