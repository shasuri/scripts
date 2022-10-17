#!/bin/bash

usage ()
{
	echo 'Usage: remove_pattern [path] <option>'
	echo 'If there is "/" end of the path, it will be ignored.'
	echo -e '\n-g	include .git directory'
	echo -e '\n-e	remove except following patterns'

	exit 1
}


# if [ $# -eq 0 ]
# 	usage

# elif [ "$1" == "-g" ]
# then
# 	# remove binary files in all sub directories
# 	files=`find ${2} ! -name "*.*"`
# else
# 	# remove except in .git directory
# 	files=`find ${1} ! \( -path ${1}/.git -prune \) -type f ! -name "*.*"`
# fi

gitopt=" ! \( -path ${1}/.git -prune \) "
exopt=""

while getopts ":hge:" option; do
   	case $option in
		h) # display Help
			usage
			exit;;
		g)
			gitopt=""
		;;
		e)
			exopt=" -type f ! \( -name "
			INDEX=0
			for i in $OPTARG
			do
				if [ $INDEX -eq 0]
					exopt+="$i"
				fi
				exopt+="-or -name $i"
				INDEX = $[ $INDEX + 1 ]
			done
			exopt+=" \)"
		;;
		\?)
			echo "Error : Invalid option!"
			exit;;
   esac
done

head="find ${1} "
tail=""

shift $[ $OPTIND - 1 ]
INDEX=0
for param in "$@"
do
	if [ $INDEX -eq 0]
		tail+=" -type f \( -name $param"
	fi
	tail+="-or -name $param"
	INDEX = $[ $INDEX + 1 ]
done
tail+=" \)"

files=`$head$gitopt$exopt$tail`

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
