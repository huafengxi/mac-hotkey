#!/usr/bin/env python3
'''
cat a.txt | ./filt.py
'''
import sys
sys.path.extend(['x-pylib'])
import locale
locale.setlocale(locale.LC_ALL, 'C')

import AppKit
info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSUIElement"] = "1"

import os
class FocusSteal:
    def __init__(self):
        pass
    def hide(self):
        self.last.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        # AppKit.NSApplication.sharedApplication().deactivate()
    def unhide(self):
        self.last = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
        # AppKit.NSApplication.sharedApplication().unhide()
    def focus(self):
        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
    def unfocus(self):
        AppKit.NSApplication.sharedApplication().deactivate()

import sys, os, re
def query(lines, pat):
    def filt_line(lines, pat):
        for line in lines:
            if re.search(pat, line, re.M):
                yield line
    def parse_pat(pat):
        m = re.match('^(.+?)\r(.?)$', pat)
        return m and m.groups() or (pat, '')
    idx_str = '0123456789abcdefghijklmnopqrstuvwxyz'
    def select_by_idx(items, idx):
        if not idx: return ''
        idx = idx_str.find(idx.replace('\r', '0'))
        return idx >= 0 and items[idx:idx+1] or []
    pat, hit = parse_pat(pat)
    items = list(filt_line(lines, pat))
    if hit:
        hit = select_by_idx(items, hit)
        return hit or ['empty', 'empty', 'empty']
    elif len(items) <= 1:
        return items
    else:
        return ['%s. %s'%(idx, item) for idx, item in zip(idx_str, items)]

def parse_lines(text, reg_pat):
    return re.findall('^\s*%s\s*\n'%(reg_pat), text, re.M)


import threading
class ResultGet:
    def __init__(self):
        self.x, self.is_end, self.c = None, False, threading.Condition()
    def reset(self):
        self.x, self.is_end = None, False
    def get(self):
        self.c.acquire()
        while not self.is_end:
            self.c.wait()
        ret = self.x
        self.c.release()
        return ret
    def set(self, x):
        self.c.acquire()
        self.x = x
        self.c.release()
    def end(self):
        self.c.acquire()
        self.is_end = True
        self.c.notify()
        self.c.release()

import wx
import string
class KeySeq:
    def __init__(self):
        self.str = ''
    def set(self, str):
        self.init = True
        self.str = str
        return str
    def get(self):
        return self.str
    def append(self, e):
        c = e.GetKeyCode()
        if e.GetKeyCode() == wx.WXK_BACK: 
            if self.init:
                self.str = ''
            else:
                self.str = self.str[:-1]
        elif c >= 256:
            pass
        else:
            char = chr(c)
            if char in string.printable or (char == '\r'):
                self.str += char
        self.init = False
        return self.str

class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, pos=(0,30), size=(400,800), style=wx.BORDER_SIMPLE|wx.STAY_ON_TOP, name="xboard")
        panel = wx.Panel(self, wx.ID_ANY)
        self.text_ctrl = wx.TextCtrl(panel, style=wx.TE_READONLY)
        self.list_ctrl = wx.ListCtrl(panel, style=wx.LC_LIST)
        self.key_seq = KeySeq()
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.text_ctrl, flag=wx.EXPAND)
        vbox.Add(self.list_ctrl, 1, flag=wx.EXPAND)
        panel.SetSizer(vbox)
        self.panel = panel
        self.Bind(wx.EVT_ACTIVATE, self.on_active)
        self.lines, self.result = [], ResultGet()
        self.result.end()
        self.focus_steal = FocusSteal()
        self.list_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.list_ctrl.Bind(wx.EVT_CHAR, self.on_char)

    def focus_panel(self):
        self.list_ctrl.SetFocus()
    def on_active(self, event):
        if not event.GetActive():
            self.result.end()
            self.Hide()
        else:
            self.focus_panel()
    def on_key_down(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.Hide()
        event.Skip()
    def on_char(self, event):
        pat = self.key_seq.append(event)
        self.update_list(pat)

    def filt(self, lines, init_filt):
        if not self.result.is_end:
            self.Hide() # cancel
            self.result.get()
        self.result.reset()
        self.lines = lines
        wx.CallAfter(self.popup, init_filt)
        return self.result.get() or ''
    def popup(self, init_filt):
        self.focus_steal.unhide()
        pat = self.key_seq.set(init_filt)
        self.update_list(pat)
        self.focus_panel()
        self.Show()
        self.Raise()
    def on_text_change(self, event):
        self.update_list(event.GetString())
    def update_list(self, pat):
        self.text_ctrl.SetValue(pat.replace('\r', '.'))
        self.list_ctrl.ClearAll()
        items = query(self.lines, pat)
        if len(items) == 1:
            self.result.set(items[0])
            self.focus_steal.hide()
            self.Hide()
        else:
            for idx, line in enumerate(items):
                self.list_ctrl.InsertItem(idx, line)

def filt(text):
    def safe_eval(code):
        try:
            return eval('dict(%s)'%(code))
        except Exception as e:
            return dict() 
    def parse_opt(data):
        m = re.search('#--\s*(.+?)\s*--', data)
        opt = dict(line_pat='(.+?)', init_filt='')
        if m:
            opt.update(safe_eval(m.group(1)))
        return opt
    line_pat, init_filt = '(.+?)', ''
    opt = parse_opt(text)
    return frame.filt(parse_lines(text, opt['line_pat']), opt['init_filt'])

def start_filt_thread(text):
    def filt_and_print():
        out = filt(text)
        frame.Close()
        print(out)
    t = threading.Thread(target=filt_and_print)
    t.daemon = True
    t.start()

def help():
    print(__doc__)

if __name__ == "__main__":
    (not sys.stdin.isatty() or len(sys.argv) == 2) or help() or sys.exit(1)
    app = wx.App(False)
    frame = MyForm()
    start_filt_thread(sys.stdin.read())
    app.MainLoop()
