import os
import json
from tqdm import *
for root, _, files in os.walk('../data/rq1/results_0128/deepseek-coder-33b-instruct'):
    for file in files:
        insts = []
        with open(os.path.join(root, file),'r') as reader:
            for line in reader.readlines():
                insts.append(json.loads(line))

        with open(os.path.join(root, file),'w') as writer:
            for inst in tqdm(insts):
                inst['prompt_len'] = 0
                writer.write(json.dumps(inst)+'\n')

