import pathlib
import importlib
import logging
import struct

from abc import ABC, abstractmethod
from typing import List

__all__ = ['Mps7']

class Protocol(ABC):
    @abstractmethod
    def _stucture_data(self):
        """ Structure the bytes data for decoding """
        pass

    @abstractmethod
    def _decode(self):
        """ Decode the bytes to protocol format """
        pass

    @abstractmethod
    def run(self):
        """ Run protocol on data and return JSON results """
        pass

class Mps7(Protocol):
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

    def __init__(self, data: bytes):
        """ Structure and decode byte data """
        self._data = data

        self._decode()
        # super().__init__(path)


    def _check_protocol(self):
        """ Check to make sure """
        self._header_data = self._data[:self.TOTAL_HBYTES]
        sig = ''.join([chr(i) for i in self._header_data[:self.HBYTES[0]]]).lower()

        assert sig == self.__class__.__name__.lower(), 'Protocol mismatch. Unable to structure data'

        self._decode()

    def _structure_data(self):
        """ Structure data to the class protocol format """

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
        for br in self._drecords:
            rtype = {v:k for k,v in self.RTYPE.items()}
            self._records.append((
                rtype[br[0]],
                struct.unpack('!I', bytes(br[self.RBYTES[0]:sum(self.RBYTES[:2])]))[0],
                struct.unpack('!Q', bytes(br[sum(self.RBYTES[:2]):sum(self.RBYTES[:3])]))[0],
                struct.unpack('!d', bytes(br[sum(self.RBYTES[:3]):sum(self.RBYTES)]))[0] if len(br) == self.TOTAL_RBYTES else None,
            ))
        self.LOGGER.info('Finished!')

        assert len(self._records) == len(self._drecords), 'Decoded records count does not match binary records count'
        self.LOGGER.debug('Decoded records:\n %s', '\n'.join(map(str, self._records)))

    @property
    def version(self) -> int:
        """ Get binary file protocol version """
        return self._header_data[sum(self.HBYTES[:1]):sum(self.HBYTES[:2])]

    @property
    def records(self) -> List[tuple]:
        return self._records

    def run(self):
        pass
