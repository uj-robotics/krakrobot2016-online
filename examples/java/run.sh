#!/bin/bash
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/
cd $ABSOLUTE_PATH
javac RobotWraper.java
java RobotWraper
