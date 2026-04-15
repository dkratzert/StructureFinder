r"""
This script has to be run from the main dir e.g. D:\GitHub\StructureFinder
"""
import hashlib
import subprocess
import sys
import winreg
from datetime import datetime
from pathlib import Path

app_path = str(Path(__file__).resolve().parent.parent)
main_path = str(Path(__file__).resolve().parent)
pathadd = [app_path, main_path, str(Path(app_path) / 'src')]
sys.path.extend(pathadd)

#from scripts.compile_ui_files import compile_ui
from scripts.version_numbers import disable_debug, isspath, process_iss, pypath
from structurefinder.misc.version import VERSION

print(f"Updating version numbers to version {VERSION} ...")

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
    shafile = Path(f'scripts/Output/StructureFinder-setup-x64-v{VERSION}-sha512.sha')
    shafile.unlink(missing_ok=True)
    shafile.write_text(sha)
    print(f"SHA512: {sha}")


def get_innosetup_path():
    """
    Get Inno Setup compiler path from Windows registry.
    Returns the path to ISCC.exe or None if not found.
    """
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1'),
        (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1'),
    ]

    for hkey, subkey in registry_paths:
        try:
            with winreg.OpenKey(hkey, subkey) as reg_key:
                install_location, _ = winreg.QueryValueEx(reg_key, 'InstallLocation')
                compiler_path = Path(install_location) / 'ISCC.exe'
                if compiler_path.exists():
                    return str(compiler_path)
        except (FileNotFoundError, OSError):
            continue

    return None


def make_installer():
    innosetup_compiler = get_innosetup_path()

    if innosetup_compiler is None:
        print("Error: Inno Setup 6 not found in registry.")
        sys.exit(1)

    subprocess.run([innosetup_compiler, '/Qp', f'/dMyAppVersion={VERSION}', r'scripts\strf-install_win64.iss'], check=False)


def compile_python_files():
    import compileall
    compileall.compile_dir(dir='dist', workers=2, force=True)
    compileall.compile_dir(dir='src', workers=2, force=True)


if __name__ == '__main__':
    #compile_ui()
    compile_python_files()
    # Make binary distributions:
    make_installer()

    make_shasum(f"scripts/Output/StructureFinder-setup-x64-v{VERSION}.exe")

    print(f'\nCreated version: {VERSION}')
    print(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    subprocess.call(f"scripts/Output/StructureFinder-setup-x64-v{VERSION}.exe")
