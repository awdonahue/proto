"""
Test protocols
"""

import pytest
import logging
from pathlib import Path

from protocols import Mps7

# RECORDS = [
#     { 'type': 'debit', 'unix_timestamp': 1393108945, 'userid': 4000000000000000000, 'amount': 604.274335557087 },
#     { 'type': 'debit', 'unix_timestamp': 1393108945, 'userid': 4136353673894269217, 'amount': 604.274335557087 },
#     { 'type': 'debit', 'unix_timestamp': 1393108945, 'userid': 4136353673894269217, 'amount': 604.274335557087 },
#     { 'type': 'debit', 'unix_timestamp': 1393108945, 'userid': 4136353673894269217, 'amount': 604.274335557087 },
# ]

TEST_FILE = 'mocklog.dat'


def test_success():
    """ Test success cases """

    m = Mps7(Path(TEST_FILE))

    print(m.get_header_data())

