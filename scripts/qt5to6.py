import os
import re
import shutil

PYQT5_TO_PYQT6_IMPORTS = [
    (r'from\s+PyQt5\s+import\s+(QtWidgets|QtGui|QtCore|QtSvg)', r'from PyQt6 import \1'),
    (r'import\s+PyQt5\.(QtWidgets|QtGui|QtCore|QtSvg)', r'import PyQt6.\1'),
    (r'from\s+PyQt5\.(\w+)\s+import\s+(\w+)', r'from PyQt6.\1 import \2'),
]

# Adjustments for Qt6 (e.g., enums and method renames)
COMMON_REPLACEMENTS = [
    # Methodenänderungen
    (r'\.exec_\(.*?\)', r'.exec()'),
    (r'\.translate\(', r'.tr('),
    (r'\.setSectionResizeMode\(', r'.header().setSectionResizeMode('),
    (r'\.toUtf8\(\)', r'.encode()'),
    (r'\.isSignalConnected\(', r'.signalsBlocked('),  # ggf. prüfen, nicht immer gleichwertig

    # Qt Enums – QtCore.Qt
    (r'QtCore\.Qt\.AlignVCenter', r'QtCore.Qt.AlignmentFlag.AlignVCenter'),
    (r'QtCore\.Qt\.AlignHCenter', r'QtCore.Qt.AlignmentFlag.AlignHCenter'),
    (r'QtCore\.Qt\.AlignLeft', r'QtCore.Qt.AlignmentFlag.AlignLeft'),
    (r'QtCore\.Qt\.AlignRight', r'QtCore.Qt.AlignmentFlag.AlignRight'),
    (r'QtCore\.Qt\.AlignTop', r'QtCore.Qt.AlignmentFlag.AlignTop'),
    (r'QtCore\.Qt\.AlignBottom', r'QtCore.Qt.AlignmentFlag.AlignBottom'),
    (r'QtCore\.Qt\.AlignCenter', r'QtCore.Qt.AlignmentFlag.AlignCenter'),

    (r'QtCore\.Qt\.Horizontal', r'QtCore.Qt.Orientation.Horizontal'),
    (r'QtCore\.Qt\.Vertical', r'QtCore.Qt.Orientation.Vertical'),

    (r'QtCore\.Qt\.LeftToRight', r'QtCore.Qt.LayoutDirection.LeftToRight'),
    (r'QtCore\.Qt\.RightToLeft', r'QtCore.Qt.LayoutDirection.RightToLeft'),

    # QtCore.Key – Tastatur-Enums
    (r'QtCore\.Qt\.Key_(\w+)', r'QtCore.Qt.Key.Key_\1'),

    # Mouse Buttons
    (r'QtCore\.Qt\.LeftButton', r'QtCore.Qt.MouseButton.LeftButton'),
    (r'QtCore\.Qt\.RightButton', r'QtCore.Qt.MouseButton.RightButton'),
    (r'QtCore\.Qt\.MiddleButton', r'QtCore.Qt.MouseButton.MiddleButton'),

    # ItemFlags
    (r'QtCore\.Qt\.ItemIsSelectable', r'QtCore.Qt.ItemFlag.ItemIsSelectable'),
    (r'QtCore\.Qt\.ItemIsEnabled', r'QtCore.Qt.ItemFlag.ItemIsEnabled'),
    (r'QtCore\.Qt\.ItemIsEditable', r'QtCore.Qt.ItemFlag.ItemIsEditable'),

    # WindowFlags
    (r'QtCore\.Qt\.Window', r'QtCore.Qt.WindowType.Window'),
    (r'QtCore\.Qt\.Dialog', r'QtCore.Qt.WindowType.Dialog'),
    (r'QtCore\.Qt\.Tool', r'QtCore.Qt.WindowType.Tool'),
    (r'QtCore\.Qt\.Popup', r'QtCore.Qt.WindowType.Popup'),

    # TextInteraction
    (r'QtCore\.Qt\.TextSelectableByMouse', r'QtCore.Qt.TextInteractionFlag.TextSelectableByMouse'),
    (r'QtCore\.Qt\.TextSelectableByKeyboard', r'QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard'),

    # Modifier Keys
    (r'QtCore\.Qt\.ControlModifier', r'QtCore.Qt.KeyboardModifier.ControlModifier'),
    (r'QtCore\.Qt\.ShiftModifier', r'QtCore.Qt.KeyboardModifier.ShiftModifier'),

    # Cursor
    (r'QtCore\.Qt\.WaitCursor', r'QtCore.Qt.CursorShape.WaitCursor'),
    (r'QtCore\.Qt\.ArrowCursor', r'QtCore.Qt.CursorShape.ArrowCursor'),
    (r'QtCore\.Qt\.PointingHandCursor', r'QtCore.Qt.CursorShape.PointingHandCursor'),

    # Sort order
    (r'QtCore\.Qt\.AscendingOrder', r'QtCore.Qt.SortOrder.AscendingOrder'),
    (r'(QtCore\.)[0,1]Qt\.DescendingOrder', r'QtCore.Qt.SortOrder.DescendingOrder'),


    # Signal/Slot Verbindung (wenn nötig z.B. bei PyQtSignal -> Signal)
    #(r'pyqtSignal', r'Signal'),
    #(r'pyqtSlot', r'Slot'),

    # Klassenumbenennungen
    (r'\bQRegExp\b', r'QRegularExpression'),
    (r'\bQDesktopWidget\b', r'QScreen'),  # deprecated in Qt6
]


def process_py_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    for pattern, repl in PYQT5_TO_PYQT6_IMPORTS + COMMON_REPLACEMENTS:
        content = re.sub(pattern, repl, content)

    if content != original_content:
        backup_path = filepath + '.bak'
        shutil.copy(filepath, backup_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Ported: {filepath}")
    else:
        print(f"No changes: {filepath}")


def process_ui_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Change XML namespaces or version-specific tags if needed
    content = re.sub(r'PyQt5', 'PyQt6', content)

    if content != original_content:
        backup_path = filepath + '.bak'
        shutil.copy(filepath, backup_path)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated UI file: {filepath}")
    else:
        print(f"No changes in UI: {filepath}")


def port_directory(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename.endswith('.py'):
                process_py_file(filepath)
            elif filename.endswith('.ui'):
                process_ui_file(filepath)


if __name__ == '__main__':

    project_root = r'D:\_DEV\GitHub\StructureFinder\src'
    port_directory(project_root)
