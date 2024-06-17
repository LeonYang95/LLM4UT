import json
import re
input_file = 'data/test_input.jsonl'
instances = []
with open(input_file,'r',encoding='utf-8') as reader:
    for line in reader.readlines():
        instances.append(json.loads(line.strip()))

prompt_pattern = r'// Given the Following test class:(.*?)```'
completion_pattern = r"Here are some unit tests testing the [\w]+ method in [\w]+ class:[\n](.*?)```"
for instance in instances:
    prompt = instance['prompt']
    completion = instance['completion']
    if completion != "":
        match = re.search(prompt_pattern, prompt, re.DOTALL)
        if match:
            print(match.group(1))
            test_shell = match.group(1).strip()
            completion_match = re.search(completion_pattern, completion, re.DOTALL)
            if completion_match:
                new_completion = test_shell + '\n'+completion_match.group(1)
        instance['completion'] = new_completion
        pass

with open(input_file,'w',encoding='utf-8') as writer:
    for instance in instances:
        writer.write(json.dumps(instance)+'\n')
