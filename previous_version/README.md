# Batch Rename

A macOS drag-and-drop tool for batch renaming files from a plain text configuration. Designed for professional audio/video workflows where you need to rename dozens or hundreds of files consistently.

![Before and After](01Before.jpg)

## Features

- Rename files in bulk by matching numbered shortcodes to full names
- Rename top-level folders with a configurable prefix
- Auto-appends `SRND` or `DwnMx` to detected surround/downmix subfolders
- Recurses up to 2 levels of subdirectories
- Sanitizes characters unsafe on Windows (e.g., `/` → `∕`, `:` → `：`)
- Warns on filenames exceeding 255 characters or containing Windows-unsafe characters
- Generates a results/warnings file if any issues are found

## Usage

### Drag and Drop

1. Create a plain text `.txt` configuration file (see [Configuration](#configuration) below).
2. Drag the `.txt` file onto **Adam Borecki's Batch Rename Droplet.app**.
3. The app renames files in place and shows a results summary.

> The config file must be saved as **plain text** (`.txt`), not rich text (`.rtf`).

### Command Line

```bash
php AdamBoreckiBatchRename.php /path/to/config.txt
```

## Configuration

Each line in the config file maps a shortcode to a full filename:

```
; Lines starting with ; are comments and are ignored

01 Strauss - Don Juan, Op. 20
02 Sibelius - "Swan of Tuonela" from Lemminkäinen Suite, Op. 22
03 Dvořák - Violin Concerto in A minor, Op. 53 (B.108) - I. Allegro ma non troppo
```

The shortcode is the leading portion of the existing filename (e.g., `01`, `02`). The rest of the line is the new name the file will be renamed to (extension is preserved).

### Folder Prefix

To rename the top-level folder with a date/label prefix:

```
folderPrefix = 160702 ACA Week 2

01 Strauss - Don Juan, Op. 20
02 Sibelius - "Swan of Tuonela" from Lemminkäinen Suite, Op. 22
```

### Shortcodes with Letter Suffixes

Use letter suffixes (`a`, `b`, `c`, ...) for multiple files sharing the same number:

```
07a L.V. Beethoven - String Quartet No. 14 - I. Adagio ma non troppo
07b L.V. Beethoven - String Quartet No. 14 - II. Allegro molto vivace
07c L.V. Beethoven - String Quartet No. 14 - III. Allegro moderato
```

## Demos

Five example use cases are included in the `Demos/` folder:

| Demo | Description |
|------|-------------|
| `01 Simple Demo` | Basic renaming with 12 audio files |
| `02 Non-Broadcast Concert` | Multi-format audio with folder structure |
| `03 Broadcast Concert` | Alternative folder structure |
| `04 Advanced- Shortcodes` | Letter suffixes for same-number files |
| `05 Advanced- More Folders` | Complex nested folder hierarchies |

## Requirements

- macOS 10.5+
- PHP (for command-line use)

## License

MIT — Copyright 2026 Adam Borecki
