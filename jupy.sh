#!/bin/bash

nohup jupyter notebook --no-browser &
sleep 1

LINK=$(jupyter notebook list | awk 'NR==2 { print $1}')

powershell.exe Start-Process -FilePath Chrome $LINK

echo $LINK
