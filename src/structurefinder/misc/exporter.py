from pathlib import Path
from typing import Dict, List

import gemmi as gemmi

from structurefinder.searcher.fileparser import CifFile


def export_to_cif_file(cif: Dict, filename: str):
    doc = cif_data_to_document(cif)
    write_cif_to_disk(doc, filename)


def cif_data_to_document(cif: Dict) -> gemmi.cif.Document:
    doc: gemmi.cif.Document = gemmi.cif.Document()
    title = 'exported_from_structurefinder_{}'.format(cif['data'])
    block: gemmi.cif.Block = doc.add_new_block(title)
    for key, value in cif.items():
        if key == '_loop':
            add_loop_to_block(block, value)
            continue
        if not key.startswith('_') or key == '_':
            continue
        if key == '_space_group_symop_operation_xyz':
            xyzloop = []
            for val in value.splitlines(keepends=False):
                val = replace_float_values(val)
                xyzloop.append({'_space_group_symop_operation_xyz': val})
            add_loop_to_block(block, xyzloop)
            # continue to prevent overriding loop by _space_group_symop_operation_xyz key-value pair.
            continue
        str_value = str(value)
        if not str_value:
            str_value = '?'
        block.set_pair(key, gemmi.cif.quote(str_value))
    return doc


def write_cif_to_disk(doc, filename):
    doc.write_file(filename, style=gemmi.cif.Style.Indent35)


def replace_float_values(val: str) -> str:
    val = val.replace('0.75', '3/4')
    val = val.replace('0.5', '1/2')
    val = val.replace('0.33', '1/3')
    val = val.replace('0.25', '1/4')
    val = val.replace('0.125', '1/6')
    return val


def add_loop_to_block(block: 'gemmi.cif.Block', value: List[Dict]) -> None:
    loop: Dict
    new_loop = None
    current_loop = None
    for loop in value:
        row = gemmi.cif.quote_list(list(loop.values()))
        if not current_loop:
            new_loop = block.init_loop('', list(loop.keys()))
            new_loop.add_row(row)
            current_loop = loop.keys()
        else:
            if loop.keys() == current_loop:
                new_loop.add_row(row)
            else:
                current_loop = None
    return None


if __name__ == '__main__':
    cif = CifFile()
    for num, file in enumerate(Path('./test-data').rglob('*.cif')):
        doc = gemmi.cif.Document()
        doc.source = file
        try:
            doc.parse_file(file)
        except ValueError:
            continue
        cifok = cif.parsefile(doc)
        export_to_cif_file(cif.cif_data, 'test{}.cif'.format(num))
        # if num == 2:
        #    break
