# -*- coding: utf-8 -*-
"""
    Classes and Functions which deal with the APDU Layer
    
"""
from logging import debug
from ecrterm import conv
from ecrterm.packets.bmp import BMP, LVAR, LLVAR
from ecrterm.packets.bitmaps import BITMAPS_ARGS

class _PacketRegister:
    """
        All Packets come into this register.
        Singleton for each Protocol.
    """
    # Currencies
    CC_EUR = [ 0x09, 0x78 ]
    # Command Classes
    CMD_STD = 0x6 # all standard commands, mostly ecr to pt
    CMD_SERVICE = 0x8 # commands mostly for service. mostly ecr to pt.
    CMD_PT = 0x4 # commands from pt to ecr.
    CMD_STATUS = 0x5 # only seen in 05 01 : status inquiry.
    # from pt to ecr only:
    CMD_RESP_OK = 0x80 # work done
    CMD_RESP_ERROR = 0x84 # work had errors

    def __init__(self):
        self.packets = {}

    def register(self, packet_class):
        if packet_class.cmd_class:
            # cmd_class is needed to be registered.
            if packet_class.cmd_instr is not None:
                # this packet is a specific tuple of instructions.
                # it will be registered as such
                key_str = '%s_%s' % (hex(packet_class.cmd_class), hex(packet_class.cmd_instr))
                # debug
                debug('Registered Class %s for Command Tuple ( %s, %s )'\
                      % (str(packet_class),
                         hex(packet_class.cmd_class),
                         hex(packet_class.cmd_instr)))
            else:
                # this packet handles a variety of supercommands
                key_str = '%s' % hex(packet_class.cmd_class)
                # debug
                debug('Registered Class %s for Super Command Fallback ( %s )'\
                      % (str(packet_class),
                         hex(packet_class.cmd_class)))
            self.packets[key_str] = packet_class

    def detect(self, datastream):
        # detects which class to use.
        if isinstance(datastream, basestring):
            # lets convert our string into a bytelist.
            datastream = conv.toBytes(datastream[:2])
        # read the first two bytes of the stream.
        cc, ci = datastream[:2]
        #print '<| %s %s' % (hex(cc), hex(ci))
        # now look up if we got this packet class:
        return self.packets.get('%s_%s' % (hex(cc), hex(ci)),
                                self.packets.get(
                                '%s' % (hex(cc)),
                                None))
Packets = _PacketRegister()

class APDUPacket(object):
    """
        Packet can be created by binary data or programmatically.
        Goal is to not save any binary data in the instance anymore.
        Translation from data to classes and vice versa should be fluent.
    """
    class NotEnoughData(Exception):
        """ raised if the apdu has not enough data to make sense """
        pass
    class IntegrityError(Exception):
        pass
    cmd_class = 0x6 # standard.
    cmd_instr = None
    allowed_bitmaps = None # None=All, [] = None.
    fixed_arguments = []
    fixed_values = {}

    # Initializing
    def __init__(self, *args, **kwargs):
        num_fixed = len(self.fixed_arguments or [])
        num_given = len(args or [])
        fvalues = {}
        if self.fixed_values:
            fvalues.update(self.fixed_values)
        i = 0
        while (i < num_given) and (i < num_fixed):
            # 
            fvalues[self.fixed_arguments[i]] = args[i]
            i += 1
        # the kwargs are the bitmaps.
        bitmaps = []
        for k, v in kwargs.items():
            key, klass, info = BITMAPS_ARGS.get(k, (None, None, None))
            if klass:
                bmp = klass(v)
                bmp._id = key
                bmp._descr = info
                bitmaps += [ bmp ]
            else:
                # maybe arg key?
                if k in self.fixed_arguments:
                    fvalues[k] = v
        self.fixed_values = fvalues
        self.args = args or []
        self.kwargs = kwargs or {}
        self.bitmaps = bitmaps

    def validate(self):
        # look thru all arguments: all needed fixed arguments here?
        # look thru all bitmaps: all bitmaps allowed?
        return True

    def handle_response(self, response, transmitter):
        # handle response overwrite
        pass

    #############################################
    # Serializing ###############################
    #############################################
    @classmethod
    def data_length(cls, data):
        """
            if data length l < 255: length is 1 byte.
            if data length 254 < l < 65535: length is 3 bytes.
            L = 0xFF -> following two bytes are length. 
        """
        l = len(data)
        if l > 254:
            if l > 65535:
                raise NotImplementedError, "APDU Data length cannot be bigger than 2 bytes."
            return [ 0xFF, ] + int_word_split(l)
        return [ l ]

    def enrich_fixed(self):
        """
            fixed arguments should be enriched here into the datastream.
            as to speak: serialized.
            
            by default, it will try to serialize fixed_arguments from fixed_values
        """
        self.validate()
        ds = []
        if self.fixed_arguments and self.fixed_values:
            # we have fixed arguments here
            for i in xrange(len(self.fixed_arguments)):
                val = self.fixed_values.get(self.fixed_arguments[i], None)
                if val:
                    if isinstance(val, basestring):
                        val = conv.toBytes(val)
                    elif isinstance(val, list):
                        pass
                    else:
                        val = [ val, ]
                    # now just save it into ds
                    ds += val
        return ds

    def introspect_fixed(self):
        """
            return a description of your fixed data.
        """
        return self.fixed_values

    def get_data(self):
        # getting the data of a packet means it is serialized into bytes.
        data = []
        # first, lets get the enriched fixed arguments:
        data += self.enrich_fixed()
        # now serialise all our bitmaps.
        # try to order our bitmaps after allowed_bitmaps maybe?
        for bitmap in self.bitmaps:
            # is bitmap allowed?
            # if y, 
            data += bitmap.dump()
        # last: insert the length
        return self.data_length(data) + data

    def to_list(self):
        return [ self.cmd_class, self.cmd_instr or 0 ] + self.data

    #############################################
    # Parsing ###################################
    #############################################
    def consume_fixed(self, data, length):
        """
            Overwrite this Function for your Packet to consume fixed
            arguments not represented by bitmaps.
            This data usually comes before any bitmaps are present
            and each packet has to know for itself, how to handle them.
            
            data is the whole packet data after the length part
            
            length is the given data-length coded into the packet.
        """
        # consume all fixed arguments from data here.
        # this might be very different from packet to packet.
        # if you use fixed_values as store, dont forget to save binary data.
        return data

    def set_data(self, blob):
        # setting the data of a packet means, it is parsed actually.
        # note: data does NOT containt cmd_class, cmd_instr anymore!
        # however, it DOES contain the LENGTH
        # now we introspect data
        pos = 0
        bitmaps = []
        if blob[pos] == 0xff:
            # length field is next two bytes.
            # @todo: could be wrong:
            l = (blob[pos + 1] << 8) + blob[pos + 2]
            pos += 2 # consume 2 bytes.
        else:
            l = blob[pos]
        pos += 1 # we move one byte further in all cases.
        # now we should read our data ahead to length.
        # look ahead if we have enough data.
        if len(blob) >= pos + l:
            data = blob[pos:pos + l]
        else:
            raise self.NotEnoughData, "Not enough Data to create the packet data."
        # step 1: fixed arguments.
        ## if this packet has some fixed arguments, they have to be
        ## parsed first.
        data = self.consume_fixed(data, l)
        # step 2: bitmaps.
        while data:
            bmp, data = BMP.read_stream(data)
            bitmaps += [bmp]
        self.bitmaps = bitmaps
    data = property(get_data, set_data)

    @classmethod
    def parse(cls, blob=""):
        if isinstance(blob, basestring):
            # lets convert our string into a bytelist.
            blob = conv.toBytes(blob)
        if isinstance(blob, list):
            # allright.
            # first we detect our packetclass
            Kls = Packets.detect(blob[:2])
            if Kls:
                instance = Kls()
                # fix for multipackets:
                if instance.cmd_instr == None:
                    instance.cmd_instr = blob[1]
                instance.data = blob[2:]
                if not instance.validate():
                    debug('Validation Error')
                return instance
            else:
                debug('Unknown Packet')

