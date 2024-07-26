#gen_tests.pl -g generator -p project_id -v version_id -n test_id -o out_dir -b total_budget

import sys
sys.path.extend(['.', '..'])
import subprocess
import time
from data import configuration
import os

# projects = configuration.projects
code_base = configuration.code_base
active_bugs = {}
with open(os.path.join(code_base,'baselines/bugs.csv'),'r') as reader:
    for line in reader.readlines():
        proj, bugs_str = line.strip().split(':')
        bugs =  bugs_str.strip().split(',')
        active_bugs[proj] = bugs

lst = []
for project, bugs  in active_bugs.items():
    p = subprocess.Popen([f"/bin/bash run_evosuite_coverage.sh {project}"], shell=True)
    time.sleep(1)
    lst.append(p)
for x in lst:
    x.wait()