import sys
sys.path.extend(['.', '..'])
import subprocess
import time
from data import configuration
import os

projects = configuration.projects
code_base = configuration.code_base
python_bin = configuration.python_bin


report_dir = f"{code_base}/rq3/coverage_reports"
if os.path.exists(report_dir):
    os.system(f"rm -rf {report_dir}")

lst = []
for project in projects:
    p = subprocess.Popen([f"{python_bin} {code_base}/rq3/rq3.py {project}"], shell=True)
    time.sleep(1)
    lst.append(p)
for x in lst:
    x.wait()
