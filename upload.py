#!/bin/env python
'''
./upload.py put local_file1 local_file2... # remote file has same name of local_file
cat a.file | ./upload.py put [remote_path]
cat a.file| ./upload.py cap [remot_path]
'''
import sys
import os
import re
import uuid
import urllib
from urllib.request import urlopen

def http(url, **kw):
    result = urlopen(url, urllib.urlencode(kw), timeout=3).read()
    if re.match('.*Exception:', result):
        raise Exception(result)
    return result

def gen_file_name(pat):
    return pat.replace('xxx', str(uuid.uuid4()))

def upload(content, url):
    if url.startswith('http://'):
      http('%s?v=upload'%(url), file=content)
    else:
      open(url, 'wb').write(content)
    return url

def append(text, url='capture.org'):
    if url.startswith('http://'):
      return http('%s?v=append'%(url), text=text)
    else:
      open(url, 'a').write(text)

def cap(*path):
    return append(sys.stdin.read(), *path)

def put(*file_list):
    if not sys.stdin.isatty():
        file_name = file_list and file_list[0] or gen_file_name()
        print(upload(sys.stdin.read(), gen_file_name(file_name)))
    else:
        for f in file_list:
            print(upload(open(f).read(), os.path.basename(f)))

def help(msg=''):
    print(msg)
    print(__doc__)

if __name__ == '__main__':
    len(sys.argv) >= 2  or help() or sys.exit(0)
    func = globals().get(sys.argv[1])
    callable(func) or help('%s is not callable' % (sys.argv[1])) or sys.exit(2)
    ret = func(*sys.argv[2:])
