#!/usr/bin/env python3
'''
./hotkey2.py
'''
import os
if os.getuid() != 0:
   raise Exception("hotkey need sudo priv!")
import sys
sys.path.extend(['x-pylib'])
import AppKit
class FocusSteal:
    def __init__(self):
        self.last = None
    def focus(self):
        # self.last = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        self.last = AppKit.NSWorkspace.sharedWorkspace().activeApplication()
        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
    def unfocus(self):
        AppKit.NSApplication.sharedApplication().deactivate()
        if self.last:
            last_active = AppKit.NSRunningApplication.runningApplicationWithProcessIdentifier_(self.last['NSApplicationProcessIdentifier'])
            if last_active:
                last_active.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
            self.last = None

from pynput import keyboard
import time
def regist(callback):
    focus_steal = FocusSteal()
    def enter_cmd_mode():
        focus_steal.focus()
    def leave_cmd_mode():
        focus_steal.unfocus()
    def is_leader_key(key):
        return key == keyboard.Key.cmd or key == keyboard.Key.cmd_r
    leader_press_ts = [0]
    def on_press(key):
        if key == keyboard.Key.space:
            key.char = ' '
        if is_leader_key(key):
            leader_press_ts[0] = time.time()
        else:
            leave_cmd_mode()
            if leader_press_ts[0] == 1 and hasattr(key, 'char'):
                callback(key.char)
            leader_press_ts[0] = 0
    def on_release(key):
        if time.time() - leader_press_ts[0] < 0.15 and is_leader_key(key):
            enter_cmd_mode()
            leader_press_ts[0] = 1
        else:
            leader_press_ts[0] = 0
    return keyboard.Listener(on_press=on_press, on_release=on_release)
import sys
import traceback
if __name__ == '__main__':
    def callback(char):
        sys.stderr.write("hotkey: {}\n".format(char))
        sys.stdout.write('{}\n'.format(char))
        sys.stdout.flush()
    regist(callback).start()
    sys.stderr.write("hotkey start at {}\n".format(time.strftime("%y-%m-%d %H:%M:%S")))
    while True:
        time.sleep(10)
