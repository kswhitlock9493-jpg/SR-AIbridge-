import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.license_scanner import guess_license_for_text

def test_spdx():
    text = "// SPDX-License-Identifier: MIT\nhello"
    assert guess_license_for_text(text) == "MIT"

def test_apache_sig():
    text = "Licensed under the Apache License, Version 2.0"
    assert guess_license_for_text(text) == "Apache-2.0"
