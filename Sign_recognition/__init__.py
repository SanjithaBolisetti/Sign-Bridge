"""Sign_recognition package shim for backend imports."""
from pathlib import Path
import sys

_pkg_dir = Path(__file__).resolve().parent
_data_dir = _pkg_dir / "Sign Language Recognition"
if _data_dir.exists():
    sys.path.append(str(_data_dir))
