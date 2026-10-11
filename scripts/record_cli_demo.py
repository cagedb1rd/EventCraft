"""Capture actual UTF-8 CLI output, independent of the shell's console code page."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ["recommend", "examples/inputs/lecture.json", "--output", "output/documented-selection"],
    ["all", "examples/inputs/lecture.json", "--select", "2", "--state", "output/documented-selection", "--output", "output/documented-final"],
]


def main():
    transcript = []
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for arguments in COMMANDS:
        result = subprocess.run([sys.executable, "-m", "eventcraft", *arguments], cwd=ROOT,
                                env=env, capture_output=True, check=True)
        output = result.stdout.decode("utf-8").replace("\r\n", "\n")
        transcript.append("$ eventcraft " + " ".join(arguments) + "\n" + output)
    (ROOT / "docs/recommendation-terminal.txt").write_text("\n".join(transcript), encoding="utf-8", newline="\n")
    print("Recorded successful actual CLI commands in UTF-8")


if __name__ == "__main__":
    main()
