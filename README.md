# Chapman University Performance Clip Exporter

Automates the batch export and rename of audio/video performance clips for Chapman University students, eliminating the most time-consuming part of their current Final Cut Pro workflow.

## The Problem

Students receive raw video and mastered audio for live performances. Their current workflow:

1. Overlay video and audio in Final Cut Pro
2. Reference a setlist to split the timeline into per-piece clips
3. **Manually export each clip one at a time**
4. **Manually rename each exported file**

Steps 3 and 4 are the bottleneck. FCP has no built-in batch rename on export — clips must either be renamed inside FCP before export, or renamed manually afterward.

## Approach

This project is a **uv Python CLI** that automates batch export and rename. The intended flow:

1. Student finishes editing in FCP and exports the project as **FCPXML** (File > Export XML) — a single, structured XML file describing the full timeline, all clip names, and timecodes.
2. The student runs this tool, pointing it at the FCPXML file and a setlist.
3. The tool parses the FCPXML, matches clips to setlist entries, and either:
   - Drives FCP to batch-export and rename via automation, **or**
   - Generates a rename manifest that is applied after a standard FCP batch export.

## Final Cut Pro Automation — What's Actually Possible

FCP does not expose a scriptable export API. Here is what exists:

| Method | What it does | Tradeoffs |
|---|---|---|
| **FCP native batch share** | Export all selected clips at once (File > Share) | Uses clip names as filenames; clips must be renamed inside FCP first |
| **FCPXML** | Open format describing the full timeline, clip names, timecodes | Best read/write interface; can generate timelines and extract metadata |
| **CommandPost** | Free macOS tool that automates FCP's GUI to batch export | Takes over the computer while running; appends sequential numbers to filenames |
| **AppleScript / GUI scripting** | Simulate menu clicks to trigger share | Fragile; FCP's AppleScript dictionary is almost entirely read-only |
| **SpliceKit** | Private API injection over JSON-RPC on localhost | Most powerful option; requires running a re-signed/modified copy of FCP |

**Planned approach:** Parse FCPXML to extract clip names and timecodes, then use **CommandPost** or **AppleScript GUI scripting** to drive export, followed by a Python rename pass using the setlist.

## Project Structure

```
batch-rename/
├── README.md
├── pyproject.toml          # uv project config
├── src/
│   └── batch_rename/
│       ├── __init__.py
│       ├── cli.py          # Entry point
│       ├── fcpxml.py       # Parse FCPXML for clip names + timecodes
│       ├── setlist.py      # Parse setlist (text/CSV)
│       ├── rename.py       # Apply rename rules to exported files
│       └── export.py       # Drive FCP export via AppleScript / CommandPost
├── demos/                  # Example FCPXML and setlist files
└── previous_version/       # Original batch rename droplet (unrelated)
```

## Setup

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and run
uv run batch-rename --help
```

## Usage (planned)

```bash
# Parse an FCPXML and a setlist, export and rename clips
uv run batch-rename export \
  --fcpxml "Performance.fcpxml" \
  --setlist "setlist.txt" \
  --output ~/Desktop/Exports

# Just rename already-exported files using a setlist
uv run batch-rename rename \
  --input ~/Desktop/RawExports \
  --setlist "setlist.txt"
```

## Setlist Format

Plain text, one piece per line. Line numbers correspond to clip numbers in the FCP timeline:

```
01 Strauss - Don Juan, Op. 20
02 Sibelius - Swan of Tuonela from Lemminkäinen Suite, Op. 22
03 Dvořák - Violin Concerto in A minor, Op. 53 - I. Allegro ma non troppo
```

## Status

Early planning / scaffolding phase. See issues for current work.
