"""CLI entry point for batch-rename."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import fcpxml, rename, setlist


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VIDEO_EXTENSIONS = {
    ".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mkv",
    ".wav", ".aif", ".aiff", ".mp3", ".m4a", ".flac",
}


def _collect_clips(directory: Path) -> list[Path]:
    return [
        p for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
def cli() -> None:
    """Batch export and rename Final Cut Pro performance clips."""


@cli.command()
@click.option(
    "--fcpxml", "fcpxml_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the FCPXML file exported from Final Cut Pro.",
)
@click.option(
    "--setlist", "setlist_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Plain-text setlist file (one numbered entry per line).",
)
def show(fcpxml_path: Path, setlist_path: Path) -> None:
    """Show clip info from FCPXML and setlist without renaming anything."""
    try:
        titles = setlist.parse(setlist_path)
        clips = fcpxml.parse(fcpxml_path)
    except (ValueError, Exception) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    click.echo(f"\nSetlist ({len(titles)} entries):")
    for i, t in enumerate(titles, 1):
        click.echo(f"  {i:02d}  {t}")

    click.echo(f"\nFCPXML primary-storyline clips ({len(clips)}):")
    for c in clips:
        click.echo(f"  [{float(c.offset):7.2f}s]  {c.title}")


@cli.command()
@click.option(
    "--input", "input_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory containing exported clip files.",
)
@click.option(
    "--setlist", "setlist_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Plain-text setlist file (one numbered entry per line).",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Print what would be renamed without actually renaming.",
)
def rename_clips(input_dir: Path, setlist_path: Path, dry_run: bool) -> None:
    """Rename exported clips to match setlist titles."""
    try:
        titles = setlist.parse(setlist_path)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    files = _collect_clips(input_dir)
    if not files:
        click.echo(
            f"No video/audio files found in {input_dir}.\n"
            f"Supported extensions: {', '.join(sorted(VIDEO_EXTENSIONS))}",
            err=True,
        )
        sys.exit(1)

    try:
        pairs = rename.plan(files, titles)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    action = "Would rename" if dry_run else "Renaming"
    click.echo(f"\n{action} {len(pairs)} file(s) in {input_dir}:\n")

    try:
        rename.apply(pairs, dry_run=dry_run)
    except FileExistsError as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)

    if dry_run:
        click.echo("\n(dry run — no files were changed)")
    else:
        click.echo(f"\nDone.")


@cli.command("rename-from-fcpxml")
@click.option(
    "--fcpxml", "fcpxml_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the FCPXML file exported from Final Cut Pro.",
)
@click.option(
    "--input", "input_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory containing exported clip files.",
)
@click.option(
    "--dry-run", is_flag=True, default=False,
    help="Print what would be renamed without actually renaming.",
)
def rename_from_fcpxml(fcpxml_path: Path, input_dir: Path, dry_run: bool) -> None:
    """Rename exported clips using clip titles from FCPXML (no setlist needed)."""
    try:
        clips = fcpxml.parse(fcpxml_path)
    except (ValueError, Exception) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    titles = [c.title for c in clips]
    files = _collect_clips(input_dir)

    if not files:
        click.echo(
            f"No video/audio files found in {input_dir}.",
            err=True,
        )
        sys.exit(1)

    try:
        pairs = rename.plan(files, titles)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    action = "Would rename" if dry_run else "Renaming"
    click.echo(f"\n{action} {len(pairs)} file(s) in {input_dir}:\n")

    try:
        rename.apply(pairs, dry_run=dry_run)
    except FileExistsError as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)

    if dry_run:
        click.echo("\n(dry run — no files were changed)")
    else:
        click.echo(f"\nDone.")
