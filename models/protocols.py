import struct
from pathlib import Path
from abc import ABC, abstractmethod

import chardet

from models.parser import Parser

__all__ = ['Mps7']

class Protocol(ABC, Parser):
    @abstractmethod
    def _decode_binary(self):
        """ Decode the read file binary string """
        pass

    @abstractmethod
    def run(self, logger, *args, **kwargs):
        """ Run the class protocol """
        pass

class Mps7(Protocol):
    """
    The MPS7 Protocol model
    """

    HEADER_BYTE_SIZES = {
        'protocol': 4,
        'version': 1,
        'records_count': 4,
    }

    RECORD_BYTE_SIZES = {
        'record_type': 1,
        'unix_timestamp': 4,
        'userid': 8,
        'amount': 8, # If record type is either 'debit' or 'credit'
    }

    RECORD_TYPE = {
        0 : 'debit',
        1 : 'credit',
        2 : 'startautopay',
        3 : 'endautopay',
    }

    def __init__(self, path):
        super().__init__(path)

        self.header = {}
        self.records = []

        self._decode_binary()

    def _decode_binary(self):
        if self._file_bytes is None:
            raise RuntimeError('No file bytes to decode')

        start_read = 0
        proto_read = start_read + self.HEADER_BYTE_SIZES['protocol']
        version_read = proto_read + self.HEADER_BYTE_SIZES['version']
        count_read = version_read + self.HEADER_BYTE_SIZES['records_count']

        endian_order = 'big'

        self.header['protocol'] = str(self._file_bytes[start_read:proto_read])
        self.header['version'] = int.from_bytes(self._file_bytes[proto_read:version_read], byteorder=endian_order)
        self.header['records_count'] = int.from_bytes(self._file_bytes[version_read:count_read], byteorder=endian_order)

        #TODO check protocol
        print(f'Header: {self.header}')
        print(f'Total bytes: {self._total_bytes}')
        print(f'Total records: {self.header["records_count"]}\n\n')

        header_size = sum(self.HEADER_BYTE_SIZES.values())
        # record_size = sum(self.RECORD_BYTE_SIZES.values())

        read = header_size
        while read < self._total_bytes:
            record = dict()

            record['type'] = self.RECORD_TYPE[int.from_bytes(
                self._file_bytes[read:read + self.RECORD_BYTE_SIZES['record_type']], byteorder=endian_order)]

            read += self.RECORD_BYTE_SIZES['record_type']

            record['unix_timestamp'] = int.from_bytes(
                self._file_bytes[read:read + self.RECORD_BYTE_SIZES['unix_timestamp']], byteorder=endian_order)

            read += self.RECORD_BYTE_SIZES['unix_timestamp']

            record['userid'] = int.from_bytes(
                self._file_bytes[read:read + self.RECORD_BYTE_SIZES['userid']], byteorder=endian_order)

            read += self.RECORD_BYTE_SIZES['userid']

            if record['type'] in [self.RECORD_TYPE[0], self.RECORD_TYPE[1]]:
                record['amount'], = struct.unpack(
                    '>d', self._file_bytes[read:read + self.RECORD_BYTE_SIZES['amount']])

                read += self.RECORD_BYTE_SIZES['amount']

            self.records.append(record)

    def get_all_records(self) -> list:
        print(f'Record amount: {len(self.records)}')
        for record in self.records:
            print(f'Record: {record}')

        return self.records

    def get_header_data(self) -> dict:
        """ Get protocol header information """
        return self.header

    def get_type_total(self, rtype: str) -> str:
        """ Get total count of record type """

        total = 0.0
        if rtype == self.RECORD_TYPE[0] or rtype == self.RECORD_TYPE[1]:
            for r in self.records:
                if r['type'] == rtype:
                    total += r['amount']
        elif rtype == self.RECORD_TYPE[2] or rtype == self.RECORD_TYPE[3]:
            for r in self.records:
                if r['type'] == rtype:
                    total += 1

        return total

    def get_user_balance(self, userid: int) -> str:
        """ Get users balance based on int id """

        balance = 0.0
        for r in self.records:
            if r['userid'] == userid:
                print(f'User Found!')

                if r['type'] == self.RECORD_TYPE[0]:
                    print(f'Amount: -{r["amount"]}')
                    balance -= r['amount']
                    continue

                if r['type'] == self.RECORD_TYPE[1]:
                    print(f'Amount: +{r["amount"]}')
                    balance += r['amount']
                    continue

        return balance

    def run(self, logger, *args, **kwargs):
        logger.info(f'Running protocol {self.__class__.__name__} on binary file: {self._filepath}')

        logger.info(f'Total amount debit: ${self.get_type_total(self.RECORD_TYPE[0]):.2f}')
        logger.info(f'Total amount credit: ${self.get_type_total(self.RECORD_TYPE[1]):.2f}')
        logger.info(f'Total autopay starts: {self.get_type_total(self.RECORD_TYPE[2]):.0f}')
        logger.info(f'Total autopay ends: {self.get_type_total(self.RECORD_TYPE[3]):.0f}')

        if 'userid' in kwargs.keys():
            uid = kwargs['userid']
            logger.info(f'Balance for userID {uid}: ${self.get_user_balance(uid):.2f}')
