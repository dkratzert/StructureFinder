"""
This script has to be run from the main dir e.g. D:\GitHub\StructureFinder
"""
import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

app_path = str(Path(__file__).resolve().parent.parent)
main_path = str(Path(__file__).resolve().parent)
pathadd = [app_path, main_path, str(Path(app_path) / 'src')]
sys.path.extend(pathadd)

from scripts.compile_ui_files import compile_ui  # noqa: E402
from scripts.version_numbers import disable_debug, isspath, process_iss, pypath  # noqa: E402
from structurefinder.misc.version import VERSION  # noqa: E402

print("Updating version numbers to version {} ...".format(VERSION))

for i in isspath:
    process_iss(i)

# disable all debug variables:
for i in pypath:
    disable_debug(i)

print("Version numbers updated.")


def sha512_checksum(filename, block_size=65536):
    """
    Calculates a SHA512 checksum from a file.
    """
    sha512 = hashlib.sha512()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha512.update(block)
    return sha512.hexdigest()


def make_shasum(filename):
    sha = sha512_checksum(filename)
    shafile = Path('scripts/Output/StructureFinder-setup-x64-v{}-sha512.sha'.format(VERSION))
    shafile.unlink(missing_ok=True)
    shafile.write_text(sha)
    print("SHA512: {}".format(sha))


def make_installer():
    innosetup_compiler = r'D:\Programme\Inno Setup 6/ISCC.exe'
    innosetup_compiler2 = r'C:\Program Files (x86)\Inno Setup 6/ISCC.exe'
    if not Path(innosetup_compiler).exists():
        innosetup_compiler = innosetup_compiler2
    subprocess.run([innosetup_compiler, '/Qp', f'/dMyAppVersion={VERSION}', r'scripts\strf-install_win64.iss', ])


def compile_python_files():
    import compileall
    compileall.compile_dir(dir='dist', workers=2, force=True)
    compileall.compile_dir(dir='src', workers=2, force=True)


if __name__ == '__main__':
    compile_ui()
    compile_python_files()
    # Make binary distributions:
    make_installer()

    make_shasum("scripts/Output/StructureFinder-setup-x64-v{}.exe".format(VERSION))

    print('\nCreated version: {}'.format(VERSION))
    print(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    subprocess.call("scripts/Output/StructureFinder-setup-x64-v{}.exe".format(VERSION))
