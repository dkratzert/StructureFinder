import os
import re
import time
from typing import Optional, Union

import gemmi
from PyQt5 import QtCore

from structurefinder.searcher.database_handler import StructureTable
from structurefinder.searcher.filecrawler import filewalker_walk, fill_db_with_cif_data, MyZipReader, \
    MyTarReader, fill_db_with_res_data
from structurefinder.searcher.fileparser import CifFile
from structurefinder.shelxfile.shelx import ShelXFile

DEBUG = False


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int)
    number_of_files = QtCore.pyqtSignal(int)

    def __init__(self, searchpath: str, add_res_files: bool, add_cif_files: bool, lastid: int,
                 structures: StructureTable, excludes: Optional[list] = None, standalone: Optional[bool] = False):
        super().__init__()
        self.stop = False
        self.searchpath = searchpath
        self.add_res_files = add_res_files
        self.add_cif_files = add_cif_files
        self.structures = structures
        self.lastid = lastid
        self.excludes = [] if not excludes else excludes
        self.files_indexed = 0
        if standalone:
            self.files_indexed = self.index_files()

    def index_files(self):
        return self.put_files_in_db(searchpath=self.searchpath, structures=self.structures,
                                    fillres=self.add_res_files, excludes=self.excludes,
                                    fillcif=self.add_cif_files, lastid=self.lastid)

    def put_files_in_db(self, searchpath: str = '', excludes: Union[list, None] = None, lastid: int = 1,
                        structures=None, fillcif=True, fillres=True) -> int:
        """
        Imports files from a certain directory
        """
        excludes = [] if not excludes else excludes
        if not searchpath:
            return 0
        if lastid <= 1:
            lastid = 1
        num = 1
        zipcifs = 0
        rescount = 0
        cifcount = 0
        time1 = time.perf_counter()
        patterns = ['*.cif', '*.zip', '*.tar.gz', '*.tar.bz2', '*.tgz', '*.res']
        filelist = filewalker_walk(str(searchpath), patterns, excludes=excludes)
        if DEBUG:
            print(f'Time for file list: {time.perf_counter()-time1:1} s.')
        filecount = len(filelist)
        self.number_of_files.emit(filecount)
        options = {}
        for filenum, (filepth, name) in enumerate(filelist, start=1):
            if filenum % 1000 == 0:
                print(f'{filenum} files...')
                self.structures.database.commit_db()
            if self.stop:
                self.structures.database.commit_db()
                self.finished.emit('Indexing aborted')
                return 0
            fullpath = os.path.join(filepth, name)
            options['modification_time'] = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(fullpath)))
            options['file_size'] = int(os.stat(str(fullpath)).st_size)
            cif = CifFile(options=options)
            self.progress.emit(filenum)
            if name.endswith('.cif') and fillcif:
                doc = gemmi.cif.Document()
                doc.source = fullpath
                try:
                    doc.parse_file(fullpath)
                except ValueError:
                    continue
                cifok = cif.parsefile(doc)
                if not cifok:
                    if DEBUG:
                        print(f"Could not parse (.cif): {fullpath}")
                    continue
                try:
                    tst = fill_db_with_cif_data(cif, filename=name, path=filepth, structure_id=lastid,
                                                structures=self.structures)
                except Exception as err:
                    if DEBUG:
                        print(f"{err}\nIndexing error in file {filepth}{os.path.sep}{name} - Id: {lastid}")
                        raise
                    continue
                if not tst:
                    continue
                cifcount += 1
                num += 1
                lastid += 1
                self.progress.emit(filenum)
                continue
            if (name.endswith('.zip') or name.endswith('.tar.gz') or name.endswith('.tar.bz2')
                or name.endswith('.tgz')) and fillcif:
                if fullpath.endswith('.zip'):
                    z = MyZipReader(fullpath)
                    filecount = filecount + len(z)
                    self.number_of_files.emit(filecount)
                else:
                    z = MyTarReader(fullpath)
                    filecount = filecount + len(z)
                    self.number_of_files.emit(filecount)
                for zippedfile in z:  # the list of cif files in the zip file
                    if not zippedfile:
                        continue
                    # Important here to re-initialize empty cif dictionary:
                    cif = CifFile(options=options)
                    omit = False
                    for ex in excludes:  # remove excludes
                        if re.search(ex, z.cifpath, re.I):
                            omit = True
                    if omit:
                        continue
                    cifok = cif.parsefile(zippedfile)
                    if not cifok:
                        if DEBUG:
                            print(f"Could not parse (zipped): {fullpath}")
                        continue
                    try:
                        tst = fill_db_with_cif_data(cif, filename=z.cifname, path=fullpath, structure_id=lastid,
                                                    structures=self.structures)
                    except Exception as err:
                        if DEBUG:
                            print(
                                str(err) + f"\nIndexing error in file {filepth}{os.path.sep}{name} - Id: {lastid}")
                            raise
                        continue
                    if not tst:
                        if DEBUG:
                            print('cif file not added:', fullpath)
                        continue
                    zipcifs += 1
                    cifcount += 1
                    num += 1
                    lastid += 1
                    self.progress.emit(filenum)
                continue
            if name.endswith('.res') and fillres:
                tst = None
                try:
                    res = ShelXFile(fullpath)
                except Exception as e:
                    if DEBUG:
                        print(e)
                        print(f"Could not parse (.res): {fullpath}")
                    continue
                if res:
                    tst = fill_db_with_res_data(res, filename=name, path=filepth, structure_id=lastid,
                                                structures=self.structures, options=options)
                if not tst:
                    if DEBUG:
                        print('res file not added:', fullpath)
                    continue
                num += 1
                rescount += 1
                lastid += 1
                self.progress.emit(filenum)
        self.structures.database.commit_db()
        time2 = time.perf_counter()
        self.progress.emit(filecount)
        m, s = divmod(time2 - time1, 60)
        h, m = divmod(m, 60)
        tmessage = f'Added {num - 1} files ({cifcount} cif, {rescount} res) files ({zipcifs} in compressed files) ' \
                   f'to database in: {int(h):>2d} h, {int(m):>2d} m, {s:>3.2f} s'
        print(f'      {filecount} files considered.')
        print(tmessage)
        self.finished.emit(tmessage)
        return len(structures)
