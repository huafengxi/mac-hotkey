#!/usr/bin/env python
import sys
import traceback
sys.path.extend(['x-pylib'])
error = []
if sys.version_info.major == 2 and sys.version_info.minor == 7:
   print 'python version OK'
else:
   print 'python version not support: %s'%(sys.version)
   error.append('pyversion')
def try_import(x, is_strong_deps=True):
    try:
        __import__(x)
        print 'import %s OK'%(x)
    except Exception as e:
        print 'import %s Fail'%(x)
        print traceback.format_exc()
        if is_strong_deps: error.append('import %s'%(x))

for m in 'pyperclip pynput objc pyautogui wx'.split():
    try_import(m)
try_import('PIL', False)

if error:
    print 'deps check fail: %s'%(error)
    sys.exit(1)
else:
    print 'all deps OK'
