#!/bin/bash
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
LOG=$ABSOLUTE_PATH/out.log
JAVA_FILE='RobotWraper'

echo "Init output log at $(date)" > "$LOG"
cd "$ABSOLUTE_PATH"

javac "$JAVA_FILE" >> "$LOG" 2>&1

if [ -e "./${JAVA_FILE}.class" ];then
    echo "Removing ${JAVA_FILE}.class file" >> "$LOG" 2>&1
    rm "./${JAVA_FILE}.class"
fi

javac "${JAVA_FILE}.java" >> "$LOG" 2>&1

if [ -e "./${JAVA_FILE}.class" ];then
    java "$JAVA_FILE"
else
    echo "ERROR; check $LOG"
fi
