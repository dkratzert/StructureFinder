# -*- mode: python -*-

block_cipher = None
import os


a = Analysis(['structurefinder/strf.py'],
             pathex=['structurefinder'],
             binaries=[('update.exe', '.')],
             datas=[('structurefinder/gui', 'gui'),
                    ('structurefinder/displaymol', 'displaymol'),
                    ('icons', 'icons'),
			 ],
             hiddenimports=['pg8000.__init__', 'decimal', 'six', 'uuid', 'distutils', 'gemmi',
			                'struct', 'time', 'distutils.version', 'json', 'numpy', 'ccdc', 'PyQt5.sip'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          #exclude_binaries=True,
          name='StructureFinder',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False ,
          icon='icons\\strf.ico')
#coll = COLLECT(exe,
#               a.binaries,
#               a.zipfiles,
#               a.datas,
#               strip=False,
#               upx=True,
#               name='StructureFinder')
