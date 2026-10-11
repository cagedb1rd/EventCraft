from pathlib import Path

import pytest

from eventcraft.extractors import extract
from eventcraft.renderer import browser

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def event():
    return extract(ROOT / "examples/inputs/lecture.json")


@pytest.fixture(scope="session")
def chromium():
    with browser() as instance:
        yield instance
