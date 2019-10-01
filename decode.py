import argparse
import pathlib
import importlib

import models.protocols as protos


if __name__ == '__main__':
    """ Run selected protocol, return JSON formatted results """
    parser = argparse.ArgumentParser(prog='Protocol Parser',
                                     description='Parse binary files and decode based on protocol',
                                     epilog='Supported protocols: mps7')

    parser.add_argument('file',
                        type=str,
                        help='Path to file to parse')

    args = vars(parser.parse_args())

    #TODO open file here, pass bytes data to protocol?
    bfile = pathlib.Path(args['file'])
    assert bfile.exists(), 'File does not exist. Check path or filename'

    data = bfile.read_bytes()
    result = protos.Mps7(data).run()

    print(result)
