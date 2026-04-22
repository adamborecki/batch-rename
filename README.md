# Batch Rename

A macOS app for Chapman University students to batch rename exported Final Cut Pro performance clips.

## The Problem

Students receive raw video and mastered audio for live performances. They overlay them in Final Cut Pro, then reference a concert program to split the timeline into per-piece clips. Some pieces have multiple sections (01a, 01b, 01c...).

FCP has no batch rename on export — students currently export and rename every clip manually, one at a time. This is the biggest time bottleneck in their workflow.

## The Solution

A drag-and-drop macOS app. The student:

1. Exports all clips from FCP at once via **File > Share** (batch share)
2. Opens **Batch Rename**, drops in their **setlist `.txt`** and the **folder of exported clips**
3. Reviews a preview of the renames
4. Clicks **Confirm** — all files are renamed instantly

## Setlist Format

Plain text, one numbered entry per line. Save as `.txt` (not `.rtf`).

```
; Lines starting with ; are comments and are ignored

01 Strauss - Don Juan, Op. 20
02 Sibelius - Swan of Tuonela from Lemminkäinen Suite, Op. 22
03 Dvořák - Violin Concerto in A minor, Op. 53 - I. Allegro ma non troppo
04 Dvořák - Violin Concerto in A minor, Op. 53 - II. Adagio ma non troppo
```

A demo setlist is in `demos/setlist_example.txt`.

## Project Structure

```
batch-rename/
├── app_entry.py          # PyInstaller entry point
├── build_app.py          # Builds dist/Batch Rename.app
├── Makefile              # make dev | make build | make run
├── pyproject.toml
├── src/
│   ├── bridge.py         # Python API exposed to the UI
│   ├── cli.py            # Optional CLI interface
│   ├── rename.py         # File matching and rename logic
│   ├── setlist.py        # Setlist parser
│   ├── fcpxml.py         # FCPXML parser (for future use)
│   └── ui/
│       └── index.html    # PyWebView frontend
├── demos/
│   ├── setlist_example.txt
│   └── test_clips/       # Dummy files for testing
└── previous_version/     # Original Automator droplet (unrelated)
```

## Development

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Build and launch the app
make dev

# Just launch the already-built app
make run
```

## Building the .app

```bash
make build
# → dist/Batch Rename.app
```

Distribute `dist/Batch Rename.app` to students. No Python or terminal required on their end.

## Roadmap

- **Concert program parsing** — drop a PDF or photo of the program; use a local Gemma 4 model (via Ollama, free, no internet required) to extract piece titles automatically
- **Section joining** — merge per-section clips (01a + 01b + 01c) into a single file per piece using ffmpeg
- **FCPXML integration** — parse clip timecodes directly from FCP's exported XML
