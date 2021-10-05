#REM execute me from the main directory
git pull

source venv/bin/activate

DISTR="linux"
if [[ $(cat /etc/os-release |grep -c "ubuntu") -gt 0 ]]
then
  DISTR="ubuntu"
fi
if [[ $(cat /etc/os-release |grep -c "suse") -gt 0 ]]
then
  DISTR="opensuse"
fi


venv/bin/pip install pip -U

venv/bin/pip install -r requirements.txt -U

venv/bin/pyinstaller StructureFinder_linux.spec --clean -y

VER=$(cat misc/version.py | grep VERSION | cut -d ' ' -f 3)

mv dist/StructureFinder "dist/StructureFinder-v${VER}_${DISTR}"

echo "StructureFinder version ${VER} finished"
