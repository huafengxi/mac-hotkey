#!/bin/bash
url=$r7
function help() {
  echo "bash <(curl -s -N $url/mac-hotkey.sh) setup # download from url"
	echo "./mac-hotkey.sh start"
	echo "./mac-hotkey.sh stop"
	echo "./mac-hotkey.sh publish [x-pylib]"
	echo "./mac-hotkey.sh remote_setup"
	echo "./mac-hotkey.sh local_setup"
}

function publish() {
    mkdir -p ~/p
    tar zc --exclude='*.pyc' --exclude='*/.*' --exclude='*.log' --exclude=x-pylib -C $base_dir/.. xboard -O | oss.sh put ~/p/xboard.tar.gz
    if [ "$1" == 'x-pylib' ]; then
       tar zc --exclude='*.pyc' --exclude='*/.*' --exclude='*.log' x-pylib -O | oss.sh put ~/p/x-pylib.tar.gz
    fi
    oss.sh put $base_dir/mac-hotkey.sh
}

function get() {
    if [[ $1 == http* ]]; then
        curl -s -N $1
    else
        cat $1
    fi
}

function remote_install() {
   echo "download and extract to '$base_dir/xboard'"
   get $url/xboard.tar.gz | tar zx
   cd xboard
   base_dir=`pwd`
   if [ -f x-pylib/done ]; then
      echo "x-pylib already installed, use 'rm -f xboard/x-pylib/done' to force reinstall"
   else
      echo "install x-pylib"
      get $url/x-pylib.tar.gz | tar zx && touch x-pylib/done
   fi
}

function local_install_pylib() {
   echo "install-pylib"
   ./install-pylib.sh
}

function local_start() {
   if ./checkdeps.py && x-pylib/s; then
       echo "start hotkey in background"
       nohup ./mac-hotkey.sh start >/tmp/hotkey.log 2>&1 & 
   else
       echo "checkdeps fail"
       echo "mac-hotkey/mac-hotkey.sh start # start hotkey manually"
       return 1
   fi
}

function remote_setup() {
   remote_install # extract to xboard and change to xboard dir
   local_start
}

function local_setup() {
   local_install_pylib
   local_start
}

function start() {
       $base_dir/x-pylib/s -c "pkill -9 -f $base_dir/hotkey2.py"
       $base_dir/x-pylib/s -c $base_dir/hotkey2.py| $base_dir/sel.py $base_dir/hk.map ': (.*) ###%s' | $base_dir/feed2.py $base_dir/trigger.py
}

function stop() {
	echo "stop hotkey"
	pkill -9 -f $base_dir/hotkey2.py
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
