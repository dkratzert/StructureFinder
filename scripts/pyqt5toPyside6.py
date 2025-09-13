import os
import re
import shutil
import argparse

PYQT5_TO_PYSIDE6_IMPORTS = [
    (r'from PyQt5 import QtWidgets', 'from PySide6 import QtWidgets'),
    (r'from PyQt5 import QtCore', 'from PySide6 import QtCore'),
    (r'from PyQt5 import QtGui', 'from PySide6 import QtGui'),
    (r'from PyQt5 import QtSvg', 'from PySide6 import QtSvg'),
    (r'import PyQt5.QtWidgets', 'import PySide6.QtWidgets'),
    (r'import PyQt5.QtCore', 'import PySide6.QtCore'),
    (r'import PyQt5.QtGui', 'import PySide6.QtGui'),
    (r'import PyQt5.QtSvg', 'import PySide6.QtSvg'),
    (r'from PyQt5.QtCore import Qt', 'from PySide6.QtCore import Qt')
]

COMMON_REPLACEMENTS = [
    (r'Qt\.', 'QtCore.Qt.'),
    (r'QRegularExpression', 'QtCore.QRegularExpression'),
    (r'QSizePolicy\.', 'QtWidgets.QSizePolicy.'),
    (r'QFont\.', 'QtGui.QFont.'),
    (r'QPainter\.', 'QtGui.QPainter.'),
    (r'QPen\.', 'QtGui.QPen.'),
    (r'QBrush\.', 'QtGui.QBrush.'),
    # Signal/Slot changes
    (r'pyqtSignal', 'Signal'),
    (r'pyqtSlot', 'Slot'),
    # Enums
    (r'QAbstractItemView\.', 'QtWidgets.QAbstractItemView.'),
    (r'QHeaderView\.', 'QtWidgets.QHeaderView.'),
    (r'QDialog\.', 'QtWidgets.QDialog.'),
    (r'QMessageBox\.', 'QtWidgets.QMessageBox.'),
    (r'QFileDialog\.', 'QtWidgets.QFileDialog.')
]


def process_py_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    for pattern, repl in PYQT5_TO_PYSIDE6_IMPORTS + COMMON_REPLACEMENTS:
        content = re.sub(pattern, repl, content)

    # Add Signal/Slot import if used
    if ('Signal' in content or 'Slot' in content) and 'from PySide6.QtCore import Signal, Slot' not in content:
        content = re.sub(r'(from PySide6.QtCore import [^\n]*)', r'\1, Signal, Slot', content, count=1)

    if content != original_content:
        backup_path = filepath + '.bak'
        shutil.copy(filepath, backup_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Ported: {filepath}")
    else:
        print(f"No changes: {filepath}")


def walk_and_process(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                process_py_file(os.path.join(dirpath, filename))


def main():
    parser = argparse.ArgumentParser(description="Port PyQt5 codebase to PySide6 (basic imports, enums, signals/slots)")
    parser.add_argument("path", help="Path to project root")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print("Invalid path.")
        return

    walk_and_process(args.path)


if __name__ == "__main__":
    main()
