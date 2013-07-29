# -*- coding: utf-8 -*-

"""
    TLV Container Format.
    
        TAG FIELD:
            # first byte:
            # b8,b7: class visibility    
            # b6: data object constructed?
            # b5-b2: tag number.
            # b1: if 1, continue at next byte.
            
            # next byte:
            b8: last byte?
            ... number.
            
        LENGTH:
            # b8 if 0, length is a 7 bit number.
            # b8 if 1, this byte only codes how many follow.
"""
from ecrterm.packets.bmp import BMP

class TLV(BMP):
    _id = 0x06

    @classmethod
    def length(cls, length):
        """ transforms a number into a TLV Length 
            returns list of bytes 
        """
        if length >= 0x80: # 128 or more...
            # we need more than 1 byte.
            # lets see if we need only 2:
            if length > 0xff: # 256 or more..
                # 0x82 followed by high byte and low byte.
                hb = (length & 0xFF00) >> 8
                lb = length & 0xFF
                return [ 0x80 + 2, hb, lb ]
            else:
                return [0x80 + 1, length ]
        else:
            # one byte is enough.
            return [ length, ]

    def parse(self, data):
        # just find out the length and skip that stuff
        #if not data:
        #    # sometimes an empty TLV container happens.
        #    return []
        l1 = data[0]
        if l1 > 0x80:
            bytes = max(2, l1 - 0x80)
            if bytes == 2:
                # hb, lb
                hb = data[1]
                lb = data[2]
                length = (hb << 8) + lb
                data = data[3:]
            elif bytes == 1:
                # one byte.
                length = data[1]
                data = data[2:]
        else:
            length = l1
            data = data[1:]
        self._data = data[:length]
        return data[length:]

