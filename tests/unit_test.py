import os
import sys
from pathlib import Path

import pytest
os.chdir(Path(__file__).parent.parent / "src")
sys.path.insert(0, "")

import logging

def test_import():
    import interpreter
    assert interpreter.Object


