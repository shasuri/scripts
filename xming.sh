#!/bin/bash

nameSrvAdr=`cat /etc/resolv.conf | grep nameserver | awk '{print $2}'`
echo usage : source xming.sh
echo Your Nameserver Address : $nameSrvAdr

export DISPLAY=$nameSrvAdr:0

powershell.exe Xlaunch.exe -run "C:\'Program Files (x86)'\Xming\config.xlaunch"
echo Xming running...

