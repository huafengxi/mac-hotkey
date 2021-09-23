#!/usr/bin/env python

import os
import sys
sys.path.extend(['x-pylib'])
msg = sys.stdin.read()
if os.fork() > 0:
    sys.exit(0)

import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSUIElement"] = "1"
import wx
app = wx.App()
wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_ERROR)
