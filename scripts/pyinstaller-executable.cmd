cd ..
venv\Scripts\pyinstaller.exe --clean ^
                                --add-binary="C:\tools\opengl64\opengl32sw.dll;opengl32sw.dll" ^
                                --add-data="gui;gui" ^
                                --add-data="displaymol;displaymol" ^
                                --add-data="icons;icons" ^
                                --hidden-import PyQt5.sip ^
                                -n StructureFinder ^
                                -y ^
                                -i "icons/strf.ico" ^
                                --windowed ^
                                strf.py