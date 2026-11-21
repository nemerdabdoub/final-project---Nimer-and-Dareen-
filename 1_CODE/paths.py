"""paths.py - where the results are saved: always 3_EVIDENCE/<today's date>/ (next to the 1_CODE folder)."""
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_ROOT = os.path.normpath(os.path.join(HERE, "..", "3_EVIDENCE"))


def evidence_dir():
    d = os.path.join(EVIDENCE_ROOT, time.strftime("%Y-%m-%d"))
    os.makedirs(d, exist_ok=True)
    return d


def stamp():
    return time.strftime("%H%M%S")
