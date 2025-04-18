# /usr/bin/env python


from pathlib import Path

from structurefinder.misc.version import VERSION

"""
This file is for updating the various version number definitions for each STRF release
"""

isspath = ["./scripts/strf-install_win64.iss"]
pypath = ["src/structurefinder/strf.py",
          "src/structurefinder/strf_cmd.py",
          "src/structurefinder/searcher/database_handler.py",
          'src/structurefinder/searcher/db_filler.py',
          'src/structurefinder/searcher/search_worker.py',
          'src/structurefinder/searcher/misc.py',
          'src/structurefinder/searcher/cif_file.py',
          "src/structurefinder/displaymol/sdm.py",
          'src/structurefinder/ccdc/query.py'
          ]


def process_iss(filepath):
    pth = Path(filepath)
    iss_file = pth.read_text(encoding="UTF-8").split("\n")
    for num, line in enumerate(iss_file):
        if line.startswith("#define MyAppVersion"):
            l = line.split()
            l[2] = f'"{VERSION}"'
            iss_file[num] = " ".join(l)
            break
    iss_file = "\n".join(iss_file)
    print(f"windows... {VERSION}, {filepath}")
    pth.write_text(iss_file, encoding="UTF-8")


def disable_debug(filepath):
    pth = Path(filepath)
    file = pth.read_text(encoding="UTF-8", errors='ignore').split("\n")
    for num, line in enumerate(file):
        if line.startswith("DEBUG") or line.startswith("PROFILE"):
            l = line.split()
            print(f"DEBUG/PROFILE.. {l[2]}, {filepath}")
            l[2] = '{}'.format("False")
            file[num] = " ".join(l)
    iss_file = "\n".join(file)
    pth.write_text(iss_file, encoding="UTF-8")


if __name__ == "__main__":
    print(f"Updating version numbers to version {VERSION} ...")

    for i in isspath:
        process_iss(i)

    for i in pypath:
        disable_debug(i)

    print("Version numbers updated.")
