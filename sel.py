#!/usr/bin/env python
'''
echo <pat> | ./sel.py file '%s'
'''
import sys
import re
def iter_line(f):
    while True:
        line = f.readline()
        if not line:
            break
        yield line
def iter_pat(pat_pat, iter):
    for pat in iter:
        if not pat:
            continue
        yield pat_pat % (pat[:-1])

def match_line(pat, line):
    m = re.search(pat, line)
    if m:
        if not m.groups():
            return line
        else:
            return '\t'.join(m.groups())

def first(iter):
    for x in iter:
        if x:
            return x

def outline(line):
    if line:
        print line
        sys.stdout.flush()

def help():
    print __doc__

len(sys.argv) >= 2 or help() or sys.exit(1)
pat_pat = len(sys.argv) >= 3 and sys.argv[2] or '%s'
for pat in iter_pat(pat_pat, iter_line(sys.stdin)):
    matchs = (match_line(pat, line) for line in file(sys.argv[1]))
    outline(first(matchs))
