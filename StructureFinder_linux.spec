# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['strf.py'],
             pathex=['D:\\Programme\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x64', 'D:\\GitHub\\StructureFinder'],
             #binaries=[('C:\\tools\\opengl64\\opengl32sw.dll', 'opengl32sw.dll')],
             datas=[('gui', 'gui'), ('searcher', 'searcher'), ('shelxfile','shelxfile'), ('apex','apex'),
                    ('displaymol', 'displaymol'), ('icons', 'icons'), ('p4pfile','p4pfile'), 
                    ('ccdc','ccdc'), ('pg8000','pg8000'), ('misc', 'misc'), ('pymatgen', 'pymatgen')],
             hiddenimports=['pg8000', 'decimal', 'six', 'uuid', 'distutils', 
                            'json', 'apex', 'distutils.version', 'misc', 'numpy'],
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
          console=False , icon='icons\\strf.ico')
#coll = COLLECT(exe,
#               a.binaries,
#               a.zipfiles,
#               a.datas,
#               strip=False,
#               upx=True,
#               upx_exclude=[],
#               name='StructureFinder')
