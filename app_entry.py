"""PyInstaller entry point."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pathlib import Path
import webview
from batch_rename.bridge import API

# When frozen by PyInstaller, bundled files land in sys._MEIPASS
if getattr(sys, "frozen", False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).parent / "src"

UI = BASE / "batch_rename" / "ui" / "index.html"


def main():
    api = API()
    window = webview.create_window(
        "Batch Rename",
        url=UI.as_uri(),
        js_api=api,
        width=860,
        height=520,
        min_size=(700, 420),
        background_color="#0f0f0f",
    )
    api.set_window(window)
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
