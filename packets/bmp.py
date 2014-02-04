# -*- coding: utf-8 -*-
"""
    Implementation of the Bitmap Variable Layer
    
    Each variable in the protocol is saved into a bitmap.

"""
from ecrterm.common import Dumpling
from ecrterm import conv

def int_word_split(x, endian='>'): # default big endian.
    """ splits 2byte integer (sometimes called a word) into 2 byte list"""
    return conv.bs2hl(struct.pack('%sH' % endian, x & 0xFFFF))

class BMPFactory(Dumpling):
    @classmethod
    def FormatByte(cls, length=1):
        class SomeBytes(BYTE):
            _length = length
        return SomeBytes

    @classmethod
    def FormatBCDByte(cls, length=1):
        class SomeBCD(BCD):
            _length = length
        return SomeBCD

    @classmethod
    def FormatTLV(cls,):
        from tlv import TLV
        return TLV

    @classmethod
    def FormatLLVAR(cls,):
        return LLVAR

    @classmethod
    def FormatLLLVAR(cls,):
        return LLLVAR

    @classmethod
    def read_stream(cls, data):
        """
            returns a tuple, containing a bitmap and the rest of the stream.
        """
        from bitmaps import BITMAPS
        # the first byte of the stream is the bitmap type
        bitmap_type = data[0]
        data = data[1:]
        bitmap_class, bmp_key, bmp_descr = BITMAPS[bitmap_type]
        #  now read the stream out of the bitmap class.
        bmp = bitmap_class()
        bmp._id = bitmap_type
        bmp._descr = bmp_descr
        bmp._key = bmp_key
        rest = bmp.parse(data)
        if len(rest) and (len(rest) == len(data)):
            raise NotImplemented, "Bitmap Class without parsing mechanism detected"
        return bmp, rest

class BMP(BMPFactory):
    _id = 0x0
    _data = None
    _descr = ""
    _key = ''
    def get_id(self):
        return self._id or 0x0
    id = property(get_id)

    def __init__(self, data=None):
        """
            initializes a BMP and makes sure _data contains a list.
        """
        if not self._data:
            if not data:
                self._data = []
            elif isinstance(data, list):
                self._data = data
            else:
                self._data = [ data ]
        self._rangecheck()

    def value(self):
        """
            has to be overwritten.
            represents the value of this bitmap as single expression.
        """
        return self._data

    def values(self):
        """
            expresses all values this bitmap has as a list.
        """
        return [self._data, ]

    def _rangecheck(self):
        """
            checks the range of each data line in the BMP if it can be
            coded with LL length bytes.
            self.LL must be set.
        """
        pass

    def parse(self, data):
        # parses the data into this bitmap
        # returns data unparsable back
        return data

    # classmethods:
    @classmethod
    def encode_fcd(cls, x, factor=0xf0):
        """
        Each digit in the number is broken up and added to FACTOR sequentially.
        Note: x has to be a number.
        >>> [ hex(i) for i in BMP.encode_fcd( 1234 ) ]                                                                                                 
        ['0xf1', '0xf2', '0xf3', '0xf4']
        """
        return [ factor + int(i) for i in list(str(int(x)))]

    @classmethod
    def decode_fcd(cls, number_list, factor=0xf0):
        """
        tries to undigitize a number in a list.
        stays in scope as long 0x0+factor <= x <= 0x09+factor.
        """
        ret = 0
        for x in number_list:
            if x > factor - 1 and x < factor + 0xa:
                ret = ret * 10 + (x - factor)
            else:
                break
        return ret

class LVAR(BMP):
    """
        LVAR Abstract Class
        offers several helper functions to deal with the LVAR Format in
        ZVT Protocol.
        also implements bases for LLVar and LLLVar.
    """
    _id = None # the lvar does not know its id from start.
    LL = 0 #: length of length header minimum.
    _data = []

    def __init__(self, data=None):
        if isinstance(data, basestring):
            self._data = conv.bs2hl(data)
            self._rangecheck()
        else:
            super(LVAR, self).__init__(self._data)

    def _rangecheck(self):
        """
            checks the range of each data line in the BMP if it can be
            coded with LL length bytes.
            self.LL must be set.
        """
        if self.LL:
            line = self._data
            if len(str(len(str(line)))) > self.LL:
                raise IndexError, "Line too long (%s): %s" % (len(line), line)

    def value(self):
        return conv.hl2bs(self._data)

    def dump(self): # dump the bytes.
        """
            dumps the bytes of the LVAR as one list.
            the minimum length of the length header can be set with self.LL
        """
        ret = []
        if self._id:
            ret = [ self._id ]
        lines = [ self._data, ]
        for line in lines:
            l = LVAR.length(len(line))
            while len(l) < self.LL:
                l = [ 0xF0 ] + l
            if isinstance(line, basestring):
                ret += l + conv.bs2hl(line)
            elif isinstance(line, list):
                ret += l + line
            else:
                raise TypeError, "Line has unsupported type in LVAR: %s" % type(line)
        return ret

    def parse(self, data):
        """
            do the exact opposite of dump.
        """
        # read the length
        l = data[:self.LL]
        l = BMP.decode_fcd(l)
        # get the data
        data = data[self.LL:]
        self._data = data[:l] # conversion of any kinds ?
        return data[l:] # we return the rest.

    @classmethod
    def length(cls, length):
        """
        Returns the length of a_list with BMP.digitize.
        >>> print [ hex(i) for i in LVAR.length('12345678901234567890') ]
        ['0xf2', '0xf0']
        """
        return BMP.encode_fcd(length)

class LLVAR(LVAR):
    """
        each LLVar Line has a length code of FxFy,
        where length = x *10 + y
    """
    LL = 2

class LLLVAR(LVAR):
    """
        each LLLVar Line has a length code of FxFyFz,
        where length = x *100 + y*10 +z
    """
    LL = 3

class FixedLength(BMP):
    _length = 0
    def get_length(self):
        return self._length
    def set_length(self, length):
        self._length = length
    length = property(get_length, set_length)

    def parse(self, data):
        if self.length:
            self._data = data[:self.length]
            data = data[self.length:]
        return data

    def dump(self):
        ret = []
        # first encode our bitmap id.
        if self._id:
            ret = [ self._id ]
        if isinstance(self._data, basestring):
            ret += [ ord(c) for c in self._data[:self.length]]
        else:
            ret += self._data[:self.length]
        return ret

# two simple classes (BCD and BYTE)
class BCD(FixedLength):
    @classmethod
    def as_int(cls, a_list):
        ''' represent a bcd list as integer '''
        return int(''.join([str(a) for a in a_list]))
    
    @classmethod
    def bcd_split(cls, b):
        """ splits a bcd byte into a tuple of numbers """
        return ((b & 0xF0) >> 4, (b & 0x0F))

    @classmethod
    def bcd_unite(cls, t):
        """ combines a tuple of two numbers into a bcd byte """
        if len(t) == 2:
            if t[0] < 10 and t[1] < 10:
                return (t[0] << 4) + t[1]
            else:
                raise ValueError, "BCD Unite can only unify two numbers < 10"

    @classmethod
    def decode_bcd(cls, something):
        """
            BCDs save two numbers per byte
            @param something: might be a string or list of bytes
            @return: a list of numbers.
        """
        if isinstance(something, basestring):
            something = conv.bs2hl(something)
        ret = []
        for x in something:
            ret += list(cls.bcd_split(x))
        return ret

    @classmethod
    def encode_bcd(cls, something, strict=False):
        """
            @param something: a list of numbers, all < 10
            @return: a list of bytes.
            
            Note: this function fills up numbers missing with 0,
            except you tell strict to be True.
        """
        if isinstance(something, basestring):
            # you gave something like "123456"
            something = [ int(x) for x in something ]
        # check the length if even
        if len(something) % 2:
            something = [0] + something
        ret = []
        for i in xrange(len(something) / 2):
            ret += [cls.bcd_unite((something[i * 2], something[i * 2 + 1]))]
        return ret

    def __init__(self, data=None):
        if isinstance(data, int):
            data = str(data)
        if isinstance(data, basestring):
            # this bcd got instantiated with a value. lets parse it.
            self._data = BCD.encode_bcd(data)
            data = None
        else:
            super(BCD, self).__init__(data)

    def values(self):
        """
            returns the actual bcd values in a list of integers
        """
        return self.decode_bcd(self._data)

    def value(self):
        """
            returns the actual bcd value as a string
        """
        values = self.values()
        if not values:
            return ''
        #return ''.join(values)
        return '%s' * len(values) % tuple(values)

    def __repr__(self):
        return "Bitmap %s, <BCD %s>" % (self._key, self._length)

    def dump(self):
        """
            a bcd dumps itself
        """
        ret = []
        # first encode our bitmap id.
        if self._id:
            ret = [ self._id ]
        # now look up our length.
        # our data has to be same length !
        data = self._data[:]
        while len(data) < self._length:
            data = [00, ] + data
        return ret + data

class BYTE(FixedLength):
    def __repr__(self):
        return "Bitmap %s, <BYTES %s>" % (self._key, self._length)

