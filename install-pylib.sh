#!/bin/bash
if [ -f x-pylib/install-done ]; then
    echo "x-pylib install OK, 'rm -f x-pylib' to force reinstall"
else
    # make sure pip is up to date
    pip2 install -U pip
    rm -rf x-pylib && mkdir -p x-pylib
    rsync -avz deps/s x-pylib && sudo chown root x-pylib/s && sudo chmod 4775 x-pylib/s
    pip2 install -t x-pylib pyautogui pynput pyperclip wxPython && touch x-pylib/install-done
fi
