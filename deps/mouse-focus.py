#!/usr/bin/env python
import sys
sys.path.extend(['x-pylib'])
from AppKit import NSWorkspace
def get_apid():
    return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationProcessIdentifier']

import Quartz
def get_geometry(pid):
    windowList = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    for w in windowList:
        if pid == w['kCGWindowOwnerPID'] and w['kCGWindowName'] and w['kCGWindowAlpha']:
            g = w['kCGWindowBounds']
            yield int(g['X']), int(g['Y']), int(g['Height']), int(g['Width'])

def get_sorted_win(pid):
    return sorted(get_geometry(pid), key=lambda (x,y,h,w): h*w)
def get_max_win_geometry(pid):
    win_list = get_sorted_win(pid)
    return win_list and win_list[-1] or None

#import pynput
#mouse = pynput.mouse.Controller()
#def mouse_move(x, y):
#    mouse.position = (x, y)
#
#g = get_max_win_geometry(get_apid())
#if g:
#    x, y, h, w = g
#    cx, cy = x + w/2, y + h/2
#    print 'geometry: x=%d y=%d h=%d w=%d cx=%d cy=%d'%(x, y, h, w, cx, cy)
#    mouse_move(cx, cy)
