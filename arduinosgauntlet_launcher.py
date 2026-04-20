from __future__ import annotations

import os
import runpy
import sys
import traceback
import ctypes
from pathlib import Path

# Explicit imports help bundlers like PyInstaller discover required packages.
import pandas as _pandas  # noqa: F401
from PySide6 import QtCore as _QtCore  # noqa: F401
from PySide6 import QtGui as _QtGui  # noqa: F401
from PySide6 import QtWidgets as _QtWidgets  # noqa: F401


def run_script(script_path: Path) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"Required script not found: {script_path}")

    previous_cwd = Path.cwd()
    try:
        os.chdir(script_path.parent)
        runpy.run_path(str(script_path), run_name="__main__")
    finally:
        os.chdir(previous_cwd)


def main() -> None:
    if getattr(sys, "frozen", False):
        # When running as a PyInstaller one-file exe, use the exe directory,
        # not the temporary extraction directory.
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    shop_dir = src_dir / "shop"

    try:
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

        run_script(shop_dir / "edit.py")
        run_script(shop_dir / "value.py")
        run_script(src_dir / "app.py")
    except Exception:
        error_text = traceback.format_exc()
        log_path = project_root / "arduinosgauntlet_error.log"
        log_path.write_text(error_text, encoding="utf-8")
        print("\n=== ARDUINO'S GAUNTLET STARTUP ERROR ===")
        print(error_text)
        print(f"Error log written to: {log_path}")
        if getattr(sys, "frozen", False):
            ctypes.windll.user32.MessageBoxW(
                0,
                (
                    "Arduino's Gauntlet failed to start.\n\n"
                    f"See error log:\n{log_path}"
                ),
                "Arduino's Gauntlet Startup Error",
                0x10,
            )
        else:
            input("\nPress Enter to close this window...")
        raise


if __name__ == "__main__":
    main()
