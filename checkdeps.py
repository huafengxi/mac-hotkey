#!/usr/bin/env python3
import sys
import traceback
sys.path.extend(['x-pylib'])
error = []
if sys.version_info.major == 3:
   print('python version OK')
else:
   print('python version not support: {}'.format(sys.version))
   error.append('pyversion')
def try_import(x, is_strong_deps=True):
    try:
        __import__(x)
        print('import {} OK'.format(x))
    except Exception as e:
        print('import {} Fail'.format(x))
        print(traceback.format_exc())
        if is_strong_deps: error.append('import '+ x)

for m in 'pyperclip pynput objc pyautogui wx'.split():
    try_import(m)
try_import('PIL', False)

if error:
    print('deps check fail: {}'.format(error))
    sys.exit(1)
else:
    print('all deps OK')
