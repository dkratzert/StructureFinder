from pathlib import Path
from typing import Dict

import gemmi as gemmi

from searcher.fileparser import Cif


def export_to_cif(cif: Cif, filename: str):
    doc: gemmi.cif.Document = gemmi.cif.Document()
    block: gemmi.cif.Block = doc.add_new_block('exported_from_structurefinder_{}'.format(cif.cif_data['data']))
    for key, value in cif.cif_data.items():
        if key == '_loop':
            add_loop_to_block(block, value)
            continue
        if not key.startswith('_') or key == '_':
            continue
        block.set_pair(key, gemmi.cif.quote(value))
    doc.write_file(filename, style=gemmi.cif.Style.Indent35)


def add_loop_to_block(block: gemmi.cif.Block, value: Dict) -> None:
    loop: Dict
    new_loop = None
    current_loop = None
    for loop in value:
        row = [gemmi.cif.quote(x) for x in loop.values()]
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
        export_to_cif(cif, 'test{}.cif'.format(num))
