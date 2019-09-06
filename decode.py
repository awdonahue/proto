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

    # getattr(protos, protos.Mps7(data).run())

    result = protos.Mps7(data).run()

    print(result)

    # print(tuple(data))

    # p = getattr(protos, protocol.title())(data)

    # mps7 = protos.Mps7()

    # logging.basicConfig(level=logging.INFO)

    # bfile = pathlib.Path(args['file'])
    # assert bfile.exists(), 'File does not exist'

    # data = tuple(bfile.read_bytes())

    # # Separate header from all records
    # header_data = data[:TOTAL_HBYTES]
    # records_data = data[TOTAL_HBYTES:]

    # protocol = ''.join([chr(i) for i in header_data[:HBYTES[0]]]).lower()

    # logging.info('Parsed file protocol: %s', protocol)
    # assert protocol.lower() in proto.__all__, 'Unknown protocol'

    # logging.info('Structuring data based on protocol...')
    # read = 0
    # drecords = []
    # while read < len(records_data):
    #     rsize = TOTAL_RBYTES if records_data[read] in (RTYPE['debit'], RTYPE['credit']) else sum(RBYTES[:3])
    #     drecords.append(records_data[read:read+rsize])
    #     read += rsize

    # logging.info('Finished!')

    # #TODO Is the header considered a record that goes towards the records counts? We'll assume yes for now...
    # hcount, rcount = ( header_data[-1] + 1, len(drecords) )
    # logging.debug('Header records count: %i. Actual records count: %i', hcount, rcount)
    # assert hcount == rcount, 'Records count does not match headers record count'
    # logging.debug('Bytes records:\n %s', '\n'.join(map(str, drecords)))

    # # Decode the records for processing and results
    # logging.info('Decoding records bytes chunks...')
    # records = []
    # for br in drecords:
    #     rtype = {v:k for k,v in RTYPE.items()}
    #     records.append((
    #         rtype[br[0]],
    #         struct.unpack('!I', bytes(br[RBYTES[0]:sum(RBYTES[:2])]))[0],
    #         struct.unpack('!Q', bytes(br[sum(RBYTES[:2]):sum(RBYTES[:3])]))[0],
    #         struct.unpack('!d', bytes(br[sum(RBYTES[:3]):sum(RBYTES)]))[0] if len(br) == TOTAL_RBYTES else None,
    #     ))
    # logging.info('Finished!')

    # assert len(records) == len(drecords), 'Decoded records count does not match binary records count'
    # logging.debug('Decoded records:\n %s', '\n'.join(map(str, records)))
