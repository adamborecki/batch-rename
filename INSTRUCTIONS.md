# Batch Rename — Studio Instructions

## Overview

Instead of exporting and naming each clip one at a time, this workflow lets you:
1. Quickly label clips with short codes in FCP
2. Batch export everything at once
3. Use AI to generate the rename list from a photo of the program
4. Rename all files in seconds with the Batch Rename app

---

## Step 1 — Label your clips in Final Cut Pro

While your timeline is split into pieces, rename each clip with a short **shortcode** — just the number (and letter if it's a section of a piece).

**To rename a clip:** Click the clip in the browser or timeline, press **Return**, type the shortcode, press **Return** again.

### Shortcode format

| Situation | Shortcode | Example |
|---|---|---|
| Single piece | `01`, `02`, `03`... | `01`, `02`, `03` |
| Piece with sections | `07a`, `07b`, `07c`... | `07a`, `07b`, `07c` |
| Multiple camera angles | `08-1`, `08-2`... | `08-1`, `08-2` |

### Example

A concert with 5 pieces where piece 3 has 3 movements:

```
01
02
03a
03b
03c
04
05
```

---

## Step 2 — Batch export from Final Cut Pro

1. In the browser, **select all your clips** (Cmd+A)
2. Go to **File > Share > Master File**
3. Choose a destination folder (e.g. a new folder on the Desktop called `exports`)
4. Click **Next** and wait for all clips to export

You should end up with files like `01.mov`, `02.mov`, `03a.mov` etc. in your exports folder.

---

## Step 3 — Generate the setlist with AI

1. **Take a photo** of the concert program (the page listing the pieces)
2. Open [Claude](https://claude.ai) or [ChatGPT](https://chatgpt.com)
3. Upload the photo and paste this prompt:

---

> **Copy this prompt:**
>
> I need you to create a plain text setlist file for a concert recording rename workflow. Look at this concert program and list every piece in performance order.
>
> Format rules:
> - One piece per line
> - Start each line with a number (`01`, `02`, etc.)
> - If a piece has multiple movements or sections, use letter suffixes (`03a`, `03b`, `03c`)
> - Use the full proper title and composer name
> - Lines starting with `;` are comments (you can add one at the top with the concert name)
> - Do not include anything else — no headers, no explanations, just the list
>
> Example output format:
> ```
> ; Spring Concert 2025
> 01 Strauss - Don Juan, Op. 20
> 02 Sibelius - Swan of Tuonela from Lemminkäinen Suite, Op. 22
> 03a Dvořák - Violin Concerto in A minor, Op. 53 - I. Allegro ma non troppo
> 03b Dvořák - Violin Concerto in A minor, Op. 53 - II. Adagio ma non troppo
> 03c Dvořák - Violin Concerto in A minor, Op. 53 - III. Finale. Allegro giocoso
> ```
>
> The shortcode numbers must match the clip labels from Final Cut Pro exactly.

---

4. Copy the AI's response into a plain text file (TextEdit → Format > Make Plain Text) and save it as `setlist.txt`

---

## Step 4 — Rename with the app

1. Open **Batch Rename**
2. Drop your `setlist.txt` onto the left zone (or click to choose)
3. Drop your exports folder onto the right zone (or click to choose)
4. Review the preview — check that every file maps to the right title
5. Click **Confirm Rename**

---

## Troubleshooting

**"File count does not match setlist entry count"**
The number of exported clips doesn't match the number of lines in the setlist. Check that every clip has a shortcode and every shortcode has a matching setlist entry.

**"Could not match files to setlist entries"**
A file's shortcode doesn't match anything in the setlist. Check for typos — e.g. the file is `03a.mov` but the setlist has `3a` or `O3a`.

**Files are out of order in the preview**
The app sorts by shortcode, so as long as the codes are correct the order will be right. Double-check the setlist is in performance order.
