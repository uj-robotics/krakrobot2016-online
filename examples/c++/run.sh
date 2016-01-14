#!/bin/bash
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/
cd $ABSOLUTE_PATH
if [ -e ./robot.bin ];then
    make clean > /dev/null
fi
make robot
./robot.bin
