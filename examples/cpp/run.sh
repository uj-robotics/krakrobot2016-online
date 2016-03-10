#!/bin/bash
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
LOG=$ABSOLUTE_PATH/out.log

echo "Init output log at $(date)" > "$LOG"
cd "$ABSOLUTE_PATH"

if [ -e ./robot.bin ];then
    make clean  >> "$LOG" 2>&1
fi

make robot  >> "$LOG" 2>&1
if [ $? -eq 0 ]; then
    ./robot.bin
else
    echo "ERROR; check $LOG"
fi
