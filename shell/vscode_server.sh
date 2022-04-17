#!/bin/bash

if (($# < 1)); then
	echo usage : ./vscode_server yourVSCWorkspacePath
	exit 2
fi

ls ${1}

if [ $? -eq 0 ]; then
	powershell.exe code ${1}
else
	echo wrong path!
fi
# powershell.exe code yourVSCWorkspacePath
