#!/usr/bin/env python

import sys
sys.path.extend(['x-pylib'])
import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSUIElement"] = "1"
import wx
app = wx.App()
x = wx.GetTextFromUser('gets')
print x
