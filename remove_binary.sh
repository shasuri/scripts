#!/bin/bash

usage ()
{
	echo 'Usage: remove_binary <option> [path]'
	echo 'If there is "/" end of the path, it will be ignored.'
	echo -e '\n-g	include .git directory'

	exit 1
}

if [ $# -eq 1 ]
then
	# remove except in .git directory
	files=`find ${1} ! \( -path ${1}/.git -prune \) -type f ! -name "*.*"`

elif [ "$1" == "-g" ] && [ $# -eq 2 ]
then
	# remove binary files in all sub directories
	files=`find ${2} ! -name "*.*"`
else
	usage
fi



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
