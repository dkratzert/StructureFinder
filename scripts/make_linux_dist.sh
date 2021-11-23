#!/bin/bash
#REM execute me from the main directory
git pull

source venv/bin/activate

DISTR="linux"
OS_RELEASE="$(cat /etc/os-release)"

if [[ "ubuntu" == *$OS_RELEASE* ]]
then
  DISTR="ubuntu"
fi
if [[ "suse" == *$OS_RELEASE* ]]
then
  DISTR="opensuse"
fi


venv/bin/pip install pip -U

venv/bin/pip install -r requirements.txt -U

venv/bin/pyinstaller StructureFinder_linux.spec --clean -y

VER=$(cat misc/version.py | grep VERSION | cut -d ' ' -f 3)

mv dist/StructureFinder "dist/StructureFinder-v${VER}_${DISTR}"

echo "StructureFinder version ${VER} finished"
