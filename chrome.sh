#!/bin/bash
FILEPATH=Z:\\`pwd`/
powershell.exe Start-Process -FilePath Chrome $FILEPATH${1}
