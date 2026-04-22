"""macOS drag-and-drop / double-click app entry point.

Flow
----
1. If a setlist .txt file is passed as a sys.argv argument (drag onto app),
   skip the file picker and use it directly.
2. Otherwise show a Tkinter dialog to pick (a) the setlist and (b) the
   exports folder.
3. Run the rename (dry-run preview first, then confirm).
4. Show a results window.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from . import rename, setlist


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick_setlist(root: tk.Tk) -> Path | None:
    path = filedialog.askopenfilename(
        parent=root,
        title="Select your setlist (.txt)",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    return Path(path) if path else None


def _pick_folder(root: tk.Tk) -> Path | None:
    path = filedialog.askdirectory(
        parent=root,
        title="Select folder containing exported clips",
    )
    return Path(path) if path else None


VIDEO_EXTENSIONS = {
    ".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mkv",
    ".wav", ".aif", ".aiff", ".mp3", ".m4a", ".flac",
}


def _collect_clips(directory: Path) -> list[Path]:
    return [
        p for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    ]


def _show_results(root: tk.Tk, pairs: list[tuple[Path, Path]]) -> bool:
    """Show a preview of renames and ask for confirmation. Returns True if confirmed."""
    win = tk.Toplevel(root)
    win.title("Preview — confirm renames")
    win.geometry("640x420")
    win.resizable(True, True)

    tk.Label(win, text=f"Ready to rename {len(pairs)} file(s):", anchor="w",
             font=("Helvetica", 13, "bold")).pack(fill="x", padx=16, pady=(14, 4))

    box = scrolledtext.ScrolledText(win, font=("Menlo", 11), state="normal",
                                    wrap="none", height=14)
    box.pack(fill="both", expand=True, padx=16, pady=4)
    for src, dst in pairs:
        box.insert("end", f"{src.name}\n  →  {dst.name}\n\n")
    box.config(state="disabled")

    confirmed = tk.BooleanVar(value=False)

    def on_go():
        confirmed.set(True)
        win.destroy()

    def on_cancel():
        win.destroy()

    btn_frame = tk.Frame(win)
    btn_frame.pack(fill="x", padx=16, pady=10)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="right", padx=4)
    tk.Button(btn_frame, text="Rename", width=10, default="active",
              bg="#1a73e8", fg="white", command=on_go).pack(side="right", padx=4)

    win.grab_set()
    root.wait_window(win)
    return confirmed.get()


def _show_done(root: tk.Tk, count: int) -> None:
    messagebox.showinfo("Done", f"Successfully renamed {count} file(s).", parent=root)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    root = tk.Tk()
    root.withdraw()  # hide the root window; we use dialogs only

    # Check if a setlist was dragged onto the app
    dropped = [Path(a) for a in sys.argv[1:] if Path(a).suffix.lower() == ".txt"]
    setlist_path = dropped[0] if dropped else None

    if setlist_path is None:
        setlist_path = _pick_setlist(root)
        if setlist_path is None:
            sys.exit(0)

    try:
        titles = setlist.parse(setlist_path)
    except ValueError as e:
        messagebox.showerror("Setlist error", str(e), parent=root)
        sys.exit(1)

    input_dir = _pick_folder(root)
    if input_dir is None:
        sys.exit(0)

    files = _collect_clips(input_dir)
    if not files:
        messagebox.showerror(
            "No clips found",
            f"No video or audio files found in:\n{input_dir}\n\n"
            f"Supported: .mov .mp4 .wav .aif .aiff .m4v .mxf .avi .mkv .mp3 .m4a .flac",
            parent=root,
        )
        sys.exit(1)

    try:
        pairs = rename.plan(files, titles)
    except ValueError as e:
        messagebox.showerror("Mismatch", str(e), parent=root)
        sys.exit(1)

    if not _show_results(root, pairs):
        sys.exit(0)

    try:
        rename.apply(pairs, dry_run=False)
    except FileExistsError as e:
        messagebox.showerror("File exists", str(e), parent=root)
        sys.exit(1)

    _show_done(root, len(pairs))
    root.destroy()


if __name__ == "__main__":
    main()
