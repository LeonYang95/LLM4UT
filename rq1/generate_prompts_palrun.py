import sys

sys.path.extend(['.', '..'])
import subprocess
import time
lst = []
for idx in range(6):
    p = subprocess.Popen(["python3 generate_prompts.py %d" % idx], shell=True)
    time.sleep(1)
    lst.append(p)
for x in lst:
    x.wait()
