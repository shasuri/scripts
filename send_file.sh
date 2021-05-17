#!/bin/bash

scp -P 10022 ${1} ${2}@${3}:${4}
# usage : scp -P 10022 yourfile yourID@serverIP:serverPath
