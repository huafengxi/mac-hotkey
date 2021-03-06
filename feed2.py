#!/usr/bin/env python3
'''
cat a.txt | ./feed2.py ./trigger.py
'''
def iter_line(f):
    while True:
        line = f.readline()
        if not line:
            break
        yield line
 
def help(): print(__doc__)
import os
import sys
import subprocess
len(sys.argv) == 2 or help() or sys.exit(1)
for line in iter_line(sys.stdin):
    sys.stdout.write('feed: {}'.format(line))
    sys.stdout.flush()
    if os.fork() == 0:
        subprocess.Popen(sys.argv[1], shell=True, stdin=subprocess.PIPE).communicate(line.encode('utf-8'))
        sys.exit(0)
