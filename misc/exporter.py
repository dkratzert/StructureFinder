from pathlib import Path
from typing import Dict

import gemmi as gemmi

from searcher.fileparser import Cif


def export_to_cif(cif: Dict, filename: str):
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
    doc.write_file(filename, style=gemmi.cif.Style.Indent35)


def replace_float_values(val):
    val = val.replace('0.75', '3/4')
    val = val.replace('0.5', '1/2')
    val = val.replace('0.33', '1/3')
    val = val.replace('0.25', '1/4')
    val = val.replace('0.125', '1/6')
    return val


def add_loop_to_block(block: gemmi.cif.Block, value: list[Dict]) -> None:
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
    cif = Cif()
    for num, file in enumerate(Path('./test-data').rglob('*.cif')):
        cifok = cif.parsefile(file.read_text().splitlines(keepends=True))
        export_to_cif(cif.cif_data, 'test{}.cif'.format(num))
        # if num == 2:
        #    break
