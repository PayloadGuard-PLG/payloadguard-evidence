import pathlib
import sys

# Make the example kernel and its fixtures importable by the test suite.
sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parent.parent / "examples" / "dosage_calculator"),
)
