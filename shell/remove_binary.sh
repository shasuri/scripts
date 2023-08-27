#!/bin/bash

cd ${1}
files=`find . -type f ! -name "*.*" -not -path "./.git/*"`

fnum=$(echo $files | wc -w)
# fnum=`find ${1} ! \( -path ${1}/.git -prune \) -type f ! -name "*.*" | wc -w`

echo ${files}

echo "Remove above ${fnum} files? (y/n)"

read yn

if [[ "$yn" =~ [Yy] ]] ;then
    echo "Remove ${fnum} binary files."
    rm ${files}
else
    echo "Remove canceled."
fi
