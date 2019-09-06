"""
Test protocols
"""

import pytest
from pathlib import Path

from protocols import Mps7

TEST_FILE = 'txnlog.dat'


def test_mps7():
    """ Run tests for MPS7 protocol """

    m = Mps7(Path(TEST_FILE))

    assert m.header['records_count'] + 1 == len(m.records) # Adding 1 to include header
    assert m.header['version'] == m.VERSION
