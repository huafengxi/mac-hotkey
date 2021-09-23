
import logging
import os
import upload
import clipboard

class NotMatch(Exception):
    pass

def try_upload_file():
    files = clipboard.get_files()
    print('upload files: {}'.format(repr(files)))
    return '\n'.join(upload.upload(open(f, "rb").read(), os.path.basename(f)) for f in files)

def try_get_clipboard_text():
    return clipboard.get_text()

def try_upload_clipboard_img(base_dir):
    png = clipboard.get_png()
    if png:
        return upload.upload(png, base_dir + '/' + upload.gen_file_name('xxx.png'))
    else:
        print("capture no img")
        return ''

def try_append_text(text, fname):
    return upload.append(text + '\n', fname)

def format_link(path):
    if not path: return ''
    return '[[%s][%s]]'%(path, os.path.basename(path))

def format_text(text):
    if not text: return ''
    if len(text.strip().split('\n')) == 1:
        return ': %s'%(text)
    return '#+begin_example\n%s\n#+end_example\n'%(text.strip())

def capture(url, capture_filt):
    clipboard.do_copy()
    base_url = os.path.dirname(url)
    text = try_get_clipboard_text()
    text = capture_filt(text)
    path_list = try_upload_file()
    if path_list:
        clipboard.set_text(path_list)
    path = try_upload_clipboard_img(base_url)
    if path:
        clipboard.set_text(path)
    text_to_append = format_text(text) + '\n'.join(format_link(path) for path in path_list.split('\n')) + format_link(path)
    return try_append_text(text_to_append, url)
