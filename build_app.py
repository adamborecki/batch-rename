"""Build the macOS .app bundle using PyInstaller.

Usage:
    uv run python build_app.py

Output:
    dist/Batch Rename.app
"""

import subprocess
import sys

ARGS = [
    "pyinstaller",
    "--onedir",
    "--windowed",
    "--name", "Batch Rename",
    "--osx-bundle-identifier", "edu.chapman.batch-rename",
    "--osx-entitlements-file", "entitlements.plist",
    # Bundle the HTML/CSS/JS UI
    "--add-data", "src/batch_rename/ui:batch_rename/ui",
    "app_entry.py",
    "--clean",
    "--noconfirm",
]

if __name__ == "__main__":
    result = subprocess.run(["uv", "run"] + ARGS)
    sys.exit(result.returncode)
