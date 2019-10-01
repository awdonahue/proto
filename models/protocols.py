import pathlib
import importlib
import logging
import struct

from abc import ABC, abstractmethod
from typing import List

__all__ = ['Mps7']

# class Protocol(ABC):
#     @abstractmethod
#     def _stucture_data(self):
#         """ Structure the bytes data for decoding """
#         pass

#     @abstractmethod
#     def _decode(self):
#         """ Decode the bytes to protocol format """
#         pass

#     @abstractmethod
#     def run(self):
#         """ Run protocol on data and return JSON results """
#         pass

class Mps7:
    """
    Decode binary data
    """
    SIG = (77, 80, 83, 55) # MPS7

    HBYTES = (4, 1, 4) # magic, version, num_records (uint32)
    RBYTES = (1, 4, 8, 8) # type, utime (uint32), userid (uint64), amount (float64)
    TOTAL_HBYTES = sum(HBYTES)
    TOTAL_RBYTES = sum(RBYTES)

    RTYPE = {
        'debit': 0,
        'credit': 1,
        'startautopay': 2,
        'endautopay': 3,
    }

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)

    def __init__(self, data: bytes):
        """ Structure and decode byte data """
        self._data = data

        self._decode()

    def _structure_data(self):
        """ Structure data to the class protocol format """

        self._header_data = self._data[:self.TOTAL_HBYTES]
        self._records_data = self._data[self.TOTAL_HBYTES:]

        self.LOGGER.info('Structuring data based on protocol...')
        read = 0
        self._drecords = []
        while read < len(self._records_data):
            rsize = self.TOTAL_RBYTES if self._records_data[read] in (self.RTYPE['debit'], self.RTYPE['credit']) else sum(self.RBYTES[:3])
            self._drecords.append(self._records_data[read:read+rsize])
            read += rsize

        self.LOGGER.info('Finished!')

        #TODO Is the header considered a record that goes towards the records counts? We'll assume yes for now...
        hcount, rcount = ( self._header_data[-1] + 1, len(self._drecords) )
        self.LOGGER.debug('Header records count: %i. Actual records count: %i', hcount, rcount)
        assert hcount == rcount, 'Records count does not match headers record count'
        self.LOGGER.debug('Bytes records:\n %s', '\n'.join(map(str, self._drecords)))

    def _decode(self):
        """ Decode structured data for processing """
        self._structure_data()

        self.LOGGER.info('Decoding structured bytes data...')
        self._records = []
        for dr in self._drecords:
            self._records.append((
                dr[0],
                struct.unpack('!I', bytes(dr[self.RBYTES[0]:sum(self.RBYTES[:2])]))[0],
                struct.unpack('!Q', bytes(dr[sum(self.RBYTES[:2]):sum(self.RBYTES[:3])]))[0],
                struct.unpack('!d', bytes(dr[sum(self.RBYTES[:3]):sum(self.RBYTES)]))[0] if len(dr) == self.TOTAL_RBYTES else None,
            ))
        self.LOGGER.info('Finished!')

        assert len(self._records) == len(self._drecords), 'Decoded records count does not match binary records count'
        self.LOGGER.debug('Decoded records:\n %s', '\n'.join(map(str, self._records)))

    # @property
    # def version(self) -> int:
    #     """ Get binary file protocol version """
    #     return self._header_data[sum(self.HBYTES[:1]):sum(self.HBYTES[:2])]

    # @property
    # def records(self) -> List[tuple]:
    #     return self._records

    def _get_type_total(self, record_type: int) -> float:
        """ Get total count of record type """

        return sum(r[-1] if r[-1] is not None else 1 for r in self._records if r[0] == record_type)

    def _get_user_balance(self, userid: int) -> str:
        """ Get users balance based on int id """

        balance = 0.0
        for r in self._records:
            if r[2] == userid:
                if r[0] == self.RTYPE['debit']:
                    balance -= r[-1]

                elif r[0] == self.RTYPE['credit']:
                    balance += r[-1]

        return balance

    def run(self) -> dict:
        totals = {rtype: f'{self._get_type_total(self.RTYPE[rtype]):.2f}' for rtype in self.RTYPE.keys()}
        totals['user'] = self._get_user_balance(2456938384156277127)

        return totals
