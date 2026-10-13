"""Generate all ten actual poster and invitation pairs through the public pipeline."""

from pathlib import Path

from eventcraft.cli import gallery

if __name__ == "__main__":
    gallery(Path(__file__).resolve().parents[1] / "output/gallery")
