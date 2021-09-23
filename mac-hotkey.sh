#!/bin/bash
function help() {
	echo "./mac-hotkey.sh local_setup"
	echo "./mac-hotkey.sh stop"
}

function local_setup() {
   echo "install-pylib"
   ./install-pylib.sh
   if ./checkdeps.py && x-pylib/s; then
       echo "start hotkey in background"
       nohup ./mac-hotkey.sh start >/tmp/hotkey.log 2>&1 & 
   else
       echo "checkdeps fail"
       echo "mac-hotkey/mac-hotkey.sh start # start hotkey manually"
       return 1
   fi
}

function start() {
       $base_dir/x-pylib/s -c "pkill -9 -f $base_dir/hotkey2.py"
       $base_dir/x-pylib/s -c $base_dir/hotkey2.py| $base_dir/sel.py $base_dir/hk.map ': (.*) ###%s' | $base_dir/feed2.py $base_dir/trigger.py
}

function stop() {
	echo "stop hotkey"
	$base_dir/x-pylib/s -c "pkill -9 -f $base_dir/hotkey2.py"
}

exit_trap () {
    local lc="$BASH_COMMAND" rc=$?
    echo "Command [$lc] exited with code [$rc]"
}

set_exit_trap() {
    trap exit_trap EXIT
    set -e
    set -o pipefail
    set -x
}
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}
if [ -z "$r7" ]; then
    echo '$r7 not set'
    exit 1
fi
real_file=`realpath $0`
base_dir=`dirname $real_file`
if [[ $base_dir == /dev/* || $base_dir == /proc/* || $base_dir == /tmp/* ]]; then
    echo "keep run in current dir"
    base_dir=`pwd`
else
    cd $base_dir
fi
method=${1:-help}
shift
ulimit -c unlimited
if [ "$method" != "help" ]; then
    false && set_exit_trap
fi
$method $*
