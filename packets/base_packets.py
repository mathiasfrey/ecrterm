# -*- coding: utf-8 -*-
from ecrterm.packets.apdu import APDUPacket, Packets
from ecrterm.packets import bmp
from ecrterm import conv, common
from ecrterm.packets.bmp import BCD
import datetime

class Packet(APDUPacket):
    wait_for_completion = False
    completion = None
    
    def bitmaps_as_dict(self):
        ret = {}
        for r in self.bitmaps:
            ret[r._key] = r
        return ret

    def __repr__(self):
        bitmap_stati = [ {b._key: b.value()} for b in self.bitmaps ]
        introspection = self.introspect_fixed()
        if introspection:
            introspection = '*%s **%s' % (introspection,
                                          bitmap_stati)
        else:
            introspection = '**%s' % bitmap_stati
        return "%s{%s %s} %s" % (self.__class__.__name__,
                                 conv.toHexString([self.cmd_class]),
                                 conv.toHexString([self.cmd_instr]),
                                   introspection)

    def _handle_unknown_response(self, response, tm):
        print "Unknown packet response %s" % response
        tm.send_received()
        return False

    def _handle_super_response(self, response, tm):
        """
            allows a packet to handle all responses in a transmission by itself.
            returns a tuple:
             # first is if handle_super_response has an answer.
             # second is the handle_response answer.
            if first is False, second is omitted, and packet is still cared
            by handle_response itself.
            
            Standard: saves "completion" packets on self, does not tell
            anybody.
        """
        if isinstance(response, Completion) or isinstance(response, Abort):
            # some sort of completion.
            self.completion = response
        return False, False

    def handle_response(self, response, tm):
        ihandle, istatus = self._handle_super_response(response, tm)
        if ihandle:
            return istatus
        if isinstance(response, PacketReceived):
            # just continue.
            return not self.wait_for_completion
        elif isinstance(response, PacketReceivedError):
            return True
        elif isinstance(response, Completion):
            tm.send_received()
            return True
        elif isinstance(response, Abort):
            # print "Abort. CODE: %s" % response.error_code
            tm.send_received()
            return True
        elif isinstance(response, StatusInformation):
            # @todo: status infomation packets
            tm.send_received()
            return False
        elif isinstance(response, IntermediateStatusInformation):
            # @todo: extended status information packets.
            tm.send_received()
            return False
        elif isinstance(response, PrintLine):
            tm.send_received()
            return False
        elif isinstance(response, PrintTextBlock):
            tm.send_received()
            return False
        else:
            return self._handle_unknown_response(response, tm)

#### Registration ##########################################################
class Registration(Packet):
    """
        06 00
        Registration. 
        arguments: password, cc, config_byte 
        bitmaps: service_byte
    """
    cmd_class = 0x6
    cmd_instr = 0x0
    fixed_arguments = ['password', 'config_byte', 'cc']
    fixed_values = {'password': '123456',
                    'config_byte': 0xBE,
                    'cc': Packets.CC_EUR}
    wait_for_completion = True

    def validate(self):
        # look thru all arguments: all needed fixed arguments here?
        if len(self.fixed_values) < 2:
            raise Exception, "Registration Packet needs passwort and config_byte at least"
        elif len(self.fixed_values) < 3 and len(self.bitmaps) > 0:
            raise Exception, "Registration Packet needs CC if you add a bitmap"
        # look thru all bitmaps: all bitmaps allowed?
        return True

    def consume_fixed(self, data, length):
        if length < 4:
            raise Exception, "Registration needs at least 4 bytes."
        if length >= 4:
            # only password and byte
            # no cc
            self.fixed_values['password'] = ''.join([conv.toHexString([c]) for c in data[0:3]])
            self.fixed_values['config_byte'] = data[3]
        if length >= 6:
            self.fixed_values['cc'] = data[4:6]
        # rest is bitmaps
        if length > 6:
            return data[6:]
        return []

    @classmethod
    def generate_config(
            cls,
            ecr_prints_receipt=True,
            ecr_prints_admin_receipt=True, # should be true too.
            ecr_intermediate_status=True, # This is mandatory !!!!!
            ecr_controls_payment=True, # amount input possible if False.
            ecr_controls_admin=True, # admin menu on PT?
            ecr_use_print_lines=True,
            initial=0x0
                    ):
        """
            generates a config bbititmask for your register function.
            can only set bits
            in tutorials 0xba (0b10111010) is used (all but admin receipt)
        """
        ret = initial
        # 0000 0001: RFU
        # 0000 0010
        if ecr_prints_receipt:
            ret |= 0x2
        # 0000 0100
        if ecr_prints_admin_receipt:
            ret |= 0x4
        if ecr_intermediate_status:
            ret |= 0x8
        else:
            print "Note: intermediate status not requested, but mandatory in CardComplete Terminals"
        if ecr_controls_payment:
            ret |= 0x10
        # 0010 0000
        if ecr_controls_admin:
            ret |= 0x20
        # 0100 0000 : RFU
        if ecr_use_print_lines:
            ret |= 0x80
        return ret & 0xBE # make sure, we do not use RFUs

    @classmethod
    def generate_service(cls,
                         do_not_assign_service_menu_pt=False,
                         use_capitals=False,
                         initial=0x0):
        ret = initial
        # 0000 0001:
        if do_not_assign_service_menu_pt:
            ret |= 0x1
        # 0000 0010
        if use_capitals:
            ret |= 0x2
        # all other RFU.
        return ret & 0x3
Packets.register(Registration)

class Kassenbericht(Packet):
    """
        a cardcomplete packet?
    """
    cmd_class = 0x0f
    cmd_instr = 0x10
    fixed_arguments = ['password', ]
    fixed_values = {'password': '123456', }
    wait_for_completion = True

    def consume_fixed(self, data, length):
        if length >= 3:
            self.fixed_values['password'] = ''.join([conv.toHexString([c]) for c in data[0:3]])
            return data[3:]
        return []
Packets.register(Kassenbericht)


class EndOfDay(Packet):
    cmd_instr = 0x50
    fixed_arguments = ['password', ]
    fixed_values = {'password': '123456', }
    wait_for_completion = True

    def consume_fixed(self, data, length):
        if length >= 3:
            self.fixed_values['password'] = ''.join([conv.toHexString([c]) for c in data[0:3]])
            return data[3:]
        return []
Packets.register(EndOfDay)

class LogOff(Packet):
    """
        06 02 Log Off
    """
    cmd_instr = 0x2
Packets.register(LogOff)

class Initialisation(Packet):
    """
    06 93
    With this command the ECR forces the PT to execute a Network-Initialization.
    """
    cmd_instr = 0x93
    fixed_arguments = ['password', ]
    fixed_values = {'password': '123456'}
    wait_for_completion = True

    def consume_fixed(self, data, length):
        if length == 3:
            self.fixed_values['password'] = ''.join([conv.toHexString([c]) for c in data[0:3]])
        return []
Packets.register(Initialisation)

# Text Related ############################################################
class ShowText(Packet):
    """    
        06 E0
           chapters: bzt 3.2.26, pt 2.24
           Note: only line 1-4 can be used by BZT.
           bitmap: F0, duration, 0 = forever
                   F1-F8: text, 7bit ascii
    """
    cmd_instr = 0xe0
    allowed_bitmaps = ['display_duration',
                       'line1', 'line2', 'line3', 'line4',
                       'line5', 'line6', 'line7', 'line8',
                       'beeps' ]
Packets.register(ShowText)

class ShowTextIntInput(Packet):
    """
        06 E2
        text output with numerical input.
    """
    cmd_instr = 0xe2
Packets.register(ShowTextIntInput)

class Completion(Packet):
    """
        06 0F
        * Sent to the ECR to signal him getting master rights back.
        * PT>ECR
    """
    cmd_instr = 0xf
    def consume_fixed(self, data, length):
        if length == 1:
            self.fixed_values['terminal_status'] = data[0]
            return []
        elif length >= 2:
            try:
                # try to LLLVAR parse:
                l = bmp.LLLVAR()
                rest = l.parse(data)
                self.fixed_values['sw-version'] = l.value()
                if len(rest) == 1:
                    self.fixed_values['terminal-status'] = rest[0]
                    return []
                else:
                    self.fixed_values = {}
                return data
            except:
                pass
        return data
Packets.register(Completion)

class Abort(Packet):
    """ 06 1E
        usually length 1, it can have data, which represents a one byte error code"""
    cmd_instr = 0x1E
    error_code = 0

    def consume_fixed(self, data, length):
        # length should be 1, and data should contain the error code.
        if length:
            self.error_code = int(data[0])
            return data[1:]
        return []

    def enrich_fixed(self):
        """
            enrich the serialized data with fixed argument error_code
        """
        if self.error_code:
            return [ int(self.error_code) ]
        return []
Packets.register(Abort)

############### 0x04 XXXX ####################################################

class StatusInformation(Packet):
    """
        04 0F
        this one is important so i mark it here.
    """
    cmd_class = Packets.CMD_PT
    cmd_instr = 0x0f
    
    def get_end_of_day_information(self):
        """ if this status information is sent in an end of day cycle,
            it contains the end of day information, making it a type of
            subpacket of itself.
            
            @returns: a dictionary holding end-of-day information.
            
            - returns an empty dictionary if there is no total amount
            - returns total amount at least in key 'amount'
            - tries to decipher credit card data into following format:
              number-<creditcard>, turnover-<creditcard>
              creditcard being [ec-card, jcb, eurocard, amex, visa, diners, remaining]
            - receipt-number-start, receipt-number-end contain the range of receipts
            
        """
        ret = {}
        # create a dictionary of bitmaps:
        bdict = self.bitmaps_as_dict()
        # at least amount should be present:
        if not 'amount' in bdict.keys():
            return {}
        else:
            ret = {'amount': int(bdict['amount'].value()),}
        # bitmap 0x60 (totals) contains the required information.
        # another bitmap (amount) holds the amount
        if not 'totals' in bdict.keys():
            # this packet holds no detail information but an amount.
            return ret
        totals = bdict['totals']
        totals_list = totals.value()
        #totals_list = str(bdict['totals'])
        # now we build our real data our of it.
        
        # rebuild date and time.
        my_time = None
        my_date = None
        if 'time' in bdict.keys():
            #print bdict['time'].value()
            mt = str(bdict['time'].value())
            my_time = datetime.time( hour=int(mt[0:2]),
                                     minute=int(mt[2:4]),
                                     second=int(mt[4:6]),
                                     )
        if 'date_day' in bdict.keys():
            #print bdict['date'].value()
            md = str(bdict['date_day'].value())
            my_date = datetime.date( year=datetime.datetime.now().year,
                                     month=int(md[0:2]),
                                     day=int(md[2:4]),
                                     )
        ret = {'receipt-number-start': BCD.as_int( BCD.decode_bcd( totals_list[0:2] ) ),
               'receipt-number-end': BCD.as_int( BCD.decode_bcd( totals_list[2:4] ) ),
               'number-ec-card': conv.bs2hl( totals_list[4] )[0],
               'turnover-ec-card': BCD.as_int( BCD.decode_bcd( totals_list[5:5+6] ) ),
               'number-jcb': conv.bs2hl(totals_list[11])[0],
               'turnover-jcb': BCD.as_int( BCD.decode_bcd( totals_list[12:12+6] ) ),
               'number-eurocard': conv.bs2hl(totals_list[18])[0],
               'turnover-eurocard': BCD.as_int( BCD.decode_bcd( totals_list[19:19+6] ) ),
               'number-amex': conv.bs2hl(totals_list[25])[0],
               'turnover-amex': BCD.as_int( BCD.decode_bcd( totals_list[26:26+6] ) ),
               'number-visa': conv.bs2hl(totals_list[32])[0],
               'turnover-visa': BCD.as_int( BCD.decode_bcd( totals_list[33:33+6] ) ),
               'number-diners': conv.bs2hl(totals_list[39])[0],
               'turnover-diners': BCD.as_int( BCD.decode_bcd( totals_list[40:40+6] ) ),
               'number-remaining': conv.bs2hl(totals_list[46])[0],
               'turnover-remaining': BCD.as_int( BCD.decode_bcd( totals_list[47:47+6] ) ),
               'amount': int(bdict['amount'].value()),
               'turnover-amount': int(bdict['amount'].value()),
               'date': my_date,
               'time': my_time,
               'number-total': 0,
               }
        # time holds simply HHMMSS (BCD)
        # date holds simply mmdd (BCD)
        
        # adding a formatted version
        tn = 0
        for key, value in ret.items():
            if key.startswith('turnover-'):
                key_id = key.replace('turnover-', '')
                # add a key with a formatted representation.
                v = float(value) / 100.0
                ret['float-%s' % key_id] = v
            elif key.startswith('number-'):
                # add total numbers.
                tn += int(value)
        ret['number-total'] = tn
        return ret
        
Packets.register(StatusInformation)

class IntermediateStatusInformation(Packet):
    """
        04 FF
        this one is important so i mark it here.
    """
    cmd_class = Packets.CMD_PT
    cmd_instr = 0xff
    fixed_arguments = ['intermediate_status']

    def consume_fixed(self, data, length):
        """
            Status has 1 byte encoding the status.
        """
        if length:
            self.fixed_values['intermediate_status'] = data[0]
            data = data[1:]
            if length > 1:
                self.fixed_values['time_out'] = data[0] # bcd.
                data = data[1:] # can be tlv.
        return data

    def __repr__(self):
        return "IntermediateStatus{04 FF}: %s" % (
                common.INTERMEDIATE_STATUS_CODES.get(self.fixed_values.get('intermediate_status', None), 'No status'),)
Packets.register(IntermediateStatusInformation)

class PacketReceived(Packet):
    """
        80 00
        most used packet ever: Packet Received Successfully.
        PT<->ECR
    """
    cmd_class = 0x80
    cmd_instr = 0x00
Packets.register(PacketReceived)

class PacketReceivedError(Packet):
    """
        84 XX
        Some error occured receiving the packet.
    """
    cmd_class = 0x84
    cmd_instr = None
    def get_error_code(self):
        if self.cmd_instr == None:
            return 0
        return self.cmd_instr
    error_code = property(get_error_code)

    def set_error_code(self, error_code):
        self.cmd_instr = error_code

    def __repr__(self):
        return "PacketReceivedERROR{84 %s}: %s" % (
                conv.toHexString([self.error_code]),
                common.ERRORCODES.get(self.error_code, 'Unknown Error'),
                                        )
Packets.register(PacketReceivedError)


### Authorisation PAckets needed:
class Authorisation(Packet):
    """
        06 01
        If you want to authorize a transaction, this is the packet you need
        to start with. Also for reading card data in general.
    """
    cmd_class = 0x6
    cmd_instr = 0x1
    wait_for_completion = True

    allowed_bitmaps = ['amount', 'cc', 'payment_type', 'track_1',
                       'card_expire', 'card_number',
                       'track_2', 'track_3',
                       'timeout', 'max_status_infos', 'pump_nr',
                       'cvv', 'additional', 'card_type', ]
Packets.register(Authorisation)

class PrintLine(Packet):
    """
        06 D1
        Usually sent by PT to ECR telling him to print a line.
        Needed for diagnosis.
    """
    cmd_class = 0x6
    cmd_instr = 0xd1
    fixed_arguments = ['attribute', 'text']
    fixed_values = {}

    def consume_fixed(self, data, length):
        if length:
            self.fixed_values['attribute'] = int(data[0]) # attribute 1 byte
            self.fixed_values['text'] = ''.join([ chr(i) for i in data[1:] ])
            return []
        return []

    def enrich_fixed(self):
        # take attribute first
        bs = [ self.fixed_values.get('attribute', 0) ]
        bs += conv.bs2hl(self.fixed_values.get('text', ''))
        return  bs
Packets.register(PrintLine)

class PrintTextBlock(Packet):
    """
        06 D3
        Same as Printline but for a textblock.
        However, uses TLV so not used in basic implementation.
    """
    cmd_class = 0x6
    cmd_instr = 0xd3

    def consume_fixed(self, data, length):
        """
            we just print the data for now
        """
        print data
        return data
Packets.register(PrintTextBlock)

class Diagnosis(Packet):
    """
        06 70
    """
    cmd_class = 0x6
    cmd_instr = 0x70
    wait_for_completion = True

    def _handle_response(self, response, tm):
        if isinstance(response, PrintLine):
            print response._data
            tm.send_received()
            return False
Packets.register(Diagnosis)

class ActivateCardReader(Packet):
    """
        08 50
        Dieses Paket ist im CardComplete nicht implementiert. 
    """
    cmd_class = 0x8
    cmd_instr = 0x50
    fixed_arguments = ('activate',)
    fixed_values = {'activate': 0x00 }
    wait_for_completion = False
#Packets.register(ActivateCardReader)
class DeActivateCardReader(ActivateCardReader):
    fixed_values = {'activate': 0xFF}


class ReadCard(Packet):
    """
    06 C0
!!! For new implementations the ECR should not send the command Read-Card with infinite time-out,
but rather should use command Status-Readout until a card is inserted. Following this the card can
be read.
!!! Cardcomplete does not use card_type or any other stuff here.
    """

    cmd_class = 0x6
    cmd_instr = 0xc0
    wait_for_completion = True # note, we do not wait for completion actually.
    fixed_arguments = ('timeout',)
    fixed_values = {'timeout': 30, }

    def consume_fixed(self, data, length):
        if length:
            self.fixed_values['timeout'] = data[0] or 30
        return data[1:]
Packets.register(ReadCard)


class ResetTerminal(Packet):
    """
        06 18
        works.
    """
    cmd_class = 0x6
    cmd_instr = 0x18
    wait_for_completion = True
Packets.register(ResetTerminal)

class StatusEnquiry(Packet):
    """
        05 01
        
    """
    cmd_class = 0x5
    cmd_instr = 0x1
    fixed_arguments = ('password',)
    fixed_values = {'password': '123456'}
    allowed_bitmaps = ['service_byte']
    wait_for_completion = True
    def consume_fixed(self, data, length):
        if length:
            self.fixed_values['password'] = ''.join([conv.toHexString([c]) for c in data[0:3] ])
        return data[3:]
Packets.register(StatusEnquiry)

if __name__ == '__main__':
    # test the register
    from pprint import pprint
    pprint(Packets.packets)
