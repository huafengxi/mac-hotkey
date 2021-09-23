#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
echo '#!python 2+3' | ./trigger.py
'''
import sys
sys.path.extend(['x-pylib'])
import logging
import re
import string
import os
import subprocess
import traceback
import itertools
import urllib
import time

import clipboard

class Exc(str): pass
class Paste(str): pass
class Send(str): pass

def gets(): return subprocess.Popen('deps/gets.sh', shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
def msg(text): subprocess.Popen('deps/msg.sh', shell=True, stdin=subprocess.PIPE).communicate(text.encode('utf-8'))
def handle_text(text):
    if text == None:
        return ''
    elif isinstance(text, Exc):
        msg(text)
    elif isinstance(text, Paste):
        return clipboard.send_text(text)
    elif isinstance(text, Send):
        return clipboard.send_keys(text)
    else:
        return text

import capture
def do_capture(self):
    def capture_filt(text): return text
    capture.capture('capture.org', capture_filt)
    return 'reload_board("", True)'

def do_tag_capture(self):
    def capture_filt(text):
        tag = gets()
        if not tag: return
        return '{} ###{}'.format(text, tag)
    capture.capture('capture.org', capture_filt)
    return 'reload_board("", True)'


import clipboard
class Trigger:
    def __call__(self, text):
        if not text:
            print('handle empty cmd')
            return
        def remove_comment(text):
            i = text.find('##')
            if i >= 0:
                text = text[:i].strip()
            return text
        text = self.sub(remove_comment(text))
        print('trigger: {}'.format(text))
        try:
            result = self.magic_process(text)
        except Exception as e:
            result = Exc(traceback.format_exc())
        return handle_text(result)
    def magic_process(self, text):
        def magic_none(self, x): return ''
        m = re.match('#!(\w+) (.*)', text)
        if not m: return Send(text)
        handler_name, args = m.groups()
        handler = globals().get('magic_%s'%(handler_name), magic_none)
        return handler(self, args)
    def copy(self):
        return clipboard.copy()
    def sub(self, text, **kw):
        if '$text' in text or '$qtext' in text:
            copyed = self.copy()
            kw.update(text=copyed, qtext=urllib.quote_plus(copyed))
        return string.Template(text).safe_substitute(kw)

def magic_post(self, text):
    return text

def magic_launch(self, text):
    return Launch(text)

def magic_send(self, text):
    return Send(eval(text))

def magic_filt(self, code):
    text = self.copy()
    try:
        result = eval(code.strip())(text)
    except Exception as e:
        return Exc(traceback.format_exc())
    logging.info('filt: |%s| -> |%s|'%(text, result))
    return Paste(result)

def magic_python(self, code):
    try:
        return eval(code.strip())
    except Exception as e:
        return Exc(traceback.format_exc())

def magic_eval(self, code):
    output = subprocess.Popen(code, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    return self(output)

def magic_msg(self, cmd):
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    msg(output)
    
def magic_sh(self, code):
    os.system(code)

from pynput.mouse import Controller
def magic_open(self, code):
    os.system('''open -a "{}"'''.format(code))
    time.sleep(0.2)
    os.system('deps/mouse-focus.py')

def magic_url(self, url):
    return magic_sh(self, """open -a "Google Chrome" '{}'""".format(url))

def magic_popup(self, url):
    return magic_sh(self, 'open -a "Google Chrome" --app={}'.format(url))

def gpg_decrypt(text):
    return subprocess.Popen(['gpg', '-d', os.path.expanduser(text)], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')

def squeeze_space(text):
    return re.sub('[\n\r]+', '\n', re.sub('(\S)[ \t]+', r'\1 ', text))

def join_line(text):
    return text.replace('\r\n', '').replace('\n', '')

def add_prefix(text, prefix='   '):
    return re.sub('(?m)^', prefix, text)

def del_prefix(text, prefix=' +'):
    return re.sub('(?m)^{}'.format(prefix), '', text)

def create_anchor(text):
    return re.sub('^(\S+) *((?:http|https)://\S+)', r'[[\2][\1]]', text)

def link_normalize(text):
    def org_short_link(text):
        '''http://a/b/c.txt -> [[http://a/b/c.txt][c.txt]]'''
        return re.sub('(?<!\[)(?:http|https):\S+/([-_a-zA-Z0-9.]+)(?!\])', lambda m: '[[%s][%s]]'%(m.group(0), m.group(1)), text)
    def md2org_link(text):
        '''[link_desc](url) -> [[url][link_desc]]'''
        return re.sub('\[(\S+?)\]\((\S+?)\)', r'[[\2][\1]]', text)
    return org_short_link(md2org_link(text))

def split_trace(text):
    return text.replace('|', '\n')

def smart_text(text):
    text = squeeze_space(text)
    if text.count('|') > 3:
        return split_trace(text)
    if text.count('\n') == 0:
        return create_anchor(text)
    return number_list(link_normalize(text))

def number_list(text):
    no_stack = [(-1, None)]
    def get_no(x):
        while x < no_stack[-1][0]:
            no_stack.pop()
        if x > no_stack[-1][0]:
            no_stack.append((x, itertools.count(1)))
        return no_stack[-1][1].next()
    return re.sub(u'^( *)(?:([0-9]{,2}|[a-z])[ .)、]+)?([^\n]+)', lambda m: '%s%d. %s'%(m.group(1), get_no(len(m.group(1))), m.group(3)), text, flags=re.M)

def read_file(path):
    path = os.path.expanduser(path)
    with open(path) as f:
        return f.read().decode('utf8')
def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content.encode('utf8'))

def paste_normalize(text):
    if '###\n' in text:
        return text
    return '<begin>###\n' + text + '<end>\n'

def paste_next(fname):
    text = paste_normalize(read_file(fname))
    text = re.sub('^(.*)###\n(.*)\n', r'\1\n\2###\n', text, flags=re.M)
    m = re.search('^(.*)###\n', text, re.M)
    write_file(fname, text)
    return Paste(m.group(1))

def paste_prev(fname):
    text = paste_normalize(read_file(fname))
    text = re.sub('^(.*)\n(.*)###\n', r'\1###\n\2\n', text, flags=re.M)
    m = re.search('^(.*)###\n', text, re.M)
    write_file(fname, text)
    return Paste(m.group(1))

import ast
def is_expr(expr):
    try:
        ast.parse(expr, mode='eval')
        return True
    except Exception as e:
        return False

def filt_by_input(v):
    code = gets()
    if not code:
        return v
    print('input_code={}'.format(code))
    if is_expr(code):
        return eval(code)
    else:
        exec(code)
        return r

def help():
    print(__doc__)
import sys
if __name__ == '__main__':
    not sys.stdin.isatty() or help() or sys.exit(1)
    os.chdir(os.path.dirname(__file__))
    Trigger()(sys.stdin.read().strip())
