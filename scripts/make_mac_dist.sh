#REM execute me from the main directory
git pull

source venv/bin/activate

pip install pip -U

pip3 install -r requirements.txt

pyinstaller StructureFinder_mac.spec --clean -y

VER=$(cat misc/version.py | grep VERSION | cut -d ' ' -f 3)

mv dist/StructureFinder.app dist/StructureFinder-v"$VER"_macos.app

cd dist || exit
rm structurefinder
rm StructureFinder-v"$VER"_macos.app.zip

zip -rm "StructureFinder-v${VER}_macos.app.zip" "StructureFinder-v${VER}_macos.app"

echo "StructureFinder version ${VER} finished"
