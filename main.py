import argparse
import logging
from pathlib import Path

from models import protocols

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Protocol Parser',
                                     description='Parse binary files and decode based on protocol',
                                     epilog='Supported protocols: mps7')
    parser.add_argument('protocol',
                        type=str,
                        choices=['mps7'],
                        help='Protocol to decode binary')
    parser.add_argument('file',
                        type=str,
                        help='Path to file to parse')

    # Get args based on protocol passed in
    protocol_parsers = parser.add_subparsers(help='Additional args dependant on protocol')

    parser_mps7 = protocol_parsers.add_parser('mps7_args', help='MPS7 arguments')
    parser_mps7.add_argument('--userid',
                             type=int,
                             help='Get balance of specified user')

    pargs = vars(parser.parse_args())

    print(pargs)

    fpath = pargs['file']
    protocol = pargs['protocol']

    if not Path(fpath).exists():
        logging.error('File not found. Check your path or filename')
        raise SystemError(1)

    getattr(protocols, protocol.title())(Path(fpath)).run(logging, **pargs)
