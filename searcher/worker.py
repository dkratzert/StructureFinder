import os
import re
import time
from typing import Optional

from PyQt5 import QtCore

from searcher.database_handler import StructureTable
from searcher.filecrawler import excluded_names, filewalker_walk, fill_db_with_cif_data, MyZipReader, MyTarReader, \
    fill_db_with_res_data
from searcher.fileparser import Cif
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
        self.excludes = excludes
        self.files_indexed = 0
        if standalone:
            self.files_indexed = self.index_files()

    def index_files(self):
        return self.put_files_in_db(searchpath=self.searchpath, structures=self.structures,
                                    fillres=self.add_res_files, excludes=None,
                                    fillcif=self.add_cif_files, lastid=self.lastid)

    def put_files_in_db(self, searchpath: str = './', excludes: list = None, lastid: int = 1,
                        structures=None, fillcif=True, fillres=True) -> int:
        """
        Imports files from a certain directory
        """
        if self.excludes:
            excluded_names.extend(excludes)
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
        filelist = filewalker_walk(str(searchpath), patterns)
        self.number_of_files.emit(len(filelist))
        options = {}
        filecount = 1
        for filenum, (filepth, name) in enumerate(filelist, start=1):
            if self.stop:
                structures.database.commit_db()
                self.finished.emit('Indexing aborted')
                return 0
            filecount = filenum
            fullpath = os.path.join(filepth, name)
            options['modification_time'] = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(fullpath)))
            options['file_size'] = int(os.stat(str(fullpath)).st_size)
            cif = Cif(options=options)
            self.progress.emit(filecount)
            self.number_of_files.emit(filecount)
            # This is really ugly copy&pase code. TODO: refractor this:
            if name.endswith('.cif') and fillcif:
                with open(fullpath, mode='r', encoding='ascii', errors="ignore") as f:
                    try:
                        cifok = cif.parsefile(f.readlines())
                        if not cifok:
                            if DEBUG:
                                print("Could not parse: {}.".format(fullpath.encode('ascii', 'ignore')))
                            continue
                    except IndexError:
                        continue
                    if cif:  # means cif object has data inside (cif could be parsed)
                        tst = None
                        try:
                            tst = fill_db_with_cif_data(cif, filename=name, path=filepth, structure_id=lastid,
                                                        structures=structures)
                        except Exception as err:
                            if DEBUG:
                                print(
                                    str(err) + "\nIndexing error in file {}{}{} - Id: {}".format(filepth, os.path.sep,
                                                                                                 name,
                                                                                                 lastid))
                                raise
                            continue
                        if not tst:
                            continue
                        cifcount += 1
                        lastid += 1
                        num += 1
                        if lastid % 1000 == 0:
                            print('{} files ...'.format(num))
                            structures.database.commit_db()
                continue
            if (name.endswith('.zip') or name.endswith('.tar.gz') or name.endswith('.tar.bz2')
                or name.endswith('.tgz')) and fillcif:
                if fullpath.endswith('.zip'):
                    # MyZipReader defines .cif ending:
                    z = MyZipReader(fullpath)
                else:
                    z = MyTarReader(fullpath)
                for zippedfile in z:  # the list of cif files in the zip file
                    # Important here to re-initialize empty cif dictionary:
                    cif = Cif(options=options)
                    omit = False
                    for ex in excluded_names:  # remove excludes
                        if re.search(ex, z.cifpath, re.I):
                            omit = True
                    if omit:
                        continue
                    try:
                        cifok = cif.parsefile(zippedfile)
                        if not cifok:
                            if DEBUG:
                                print("Could not parse: {}.".format(fullpath.encode('ascii', 'ignore')))
                            continue
                    except IndexError:
                        continue
                    if cif:
                        tst = None
                        try:
                            tst = fill_db_with_cif_data(cif, filename=z.cifname, path=fullpath, structure_id=lastid,
                                                        structures=structures)
                        except Exception as err:
                            if DEBUG:
                                print(
                                    str(err) + "\nIndexing error in file {}{}{} - Id: {}".format(filepth, os.path.sep,
                                                                                                 name,
                                                                                                 lastid))
                                raise
                        if not tst:
                            if DEBUG:
                                print('cif file not added:', fullpath)
                            continue
                        zipcifs += 1
                        cifcount += 1
                        lastid += 1
                        num += 1
                        if lastid % 1000 == 0:
                            print('{} files ...'.format(num))
                            structures.database.commit_db()
                continue
            if name.endswith('.res') and fillres:
                tst = None
                try:
                    res = ShelXFile(fullpath)
                except Exception as e:
                    if DEBUG:
                        print(e)
                        print("Could not parse: {}.".format(fullpath.encode('ascii', 'ignore')))
                    continue
                if res:
                    tst = fill_db_with_res_data(res, filename=name, path=filepth, structure_id=lastid,
                                                structures=structures, options=options)
                if not tst:
                    if DEBUG:
                        print('res file not added:', fullpath)
                    continue
                #            if self:
                #                self.add_table_row(filename=name, path=filepth, data=name, structure_id=str(lastid))
                lastid += 1
                num += 1
                rescount += 1
                if lastid % 1000 == 0:
                    print('{} files ...'.format(num))
                    structures.database.commit_db()
        structures.database.commit_db()
        time2 = time.perf_counter()
        self.progress.emit(filecount)
        m, s = divmod(time2 - time1, 60)
        h, m = divmod(m, 60)
        tmessage = 'Added {0} files ({5} cif, {6} res) files ({4} in compressed files) to database in: ' \
                   '{1:>2d} h, {2:>2d} m, {3:>3.2f} s'
        print('      {} files considered.'.format(filecount))
        print(tmessage.format(num - 1, int(h), int(m), s, zipcifs, cifcount, rescount))
        self.finished.emit(tmessage.format(num - 1, int(h), int(m), s, zipcifs, cifcount, rescount))
        return lastid - 1
