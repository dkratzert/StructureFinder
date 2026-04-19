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
          'src/structurefinder/ccdc/query.py'
          ]


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

    for i in pypath:
        disable_debug(i)

    print("Version numbers updated.")
