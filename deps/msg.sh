#!/bin/bash
osascript 3<&0 <<EOF
on run argv
    return display alert (do shell script "cat 0<&3")
end run
EOF
