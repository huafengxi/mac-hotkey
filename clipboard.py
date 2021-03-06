import time
import pyperclip

import pyautogui
def send_keys(text):
    time.sleep(0.1)
    pyautogui.typewrite(text)

def send_text(text):
    paste(text)

def do_copy():
    pyautogui.hotkey('command', 'c')
def do_paste():
    pyautogui.hotkey('command', 'v')

def copy():
    do_copy()
    return pyperclip.paste()

def paste(text):
    pyperclip.copy(text)
    do_paste()

def get_text():
    return pyperclip.paste()
def set_text(text):
    pyperclip.copy(text)

def get_files():
    return []

from io import BytesIO
try:
    from PIL import ImageGrab
    enable_grab_img = True
except:
    enable_grab_img = False
def get_png():
    if not enable_grab_img:
        return ''
    im = ImageGrab.grabclipboard()
    if im:
      f = BytesIO()
      im.save(f, 'PNG')
      return f.getvalue()
    else:
      return ''
