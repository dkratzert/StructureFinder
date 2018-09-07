# -*- mode: python -*-

block_cipher = None


a = Analysis(['strf.py'],
             pathex=['D:\\GitHub\\StructureFinder'],
             binaries=[('C:\\tools\\opengl64', 'opengl32sw.dll')],
             datas=[('gui', 'gui'), ('displaymol', 'displaymol'), ('icons', 'icons')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='StructureFinder',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='icons\\strf.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='StructureFinder')
