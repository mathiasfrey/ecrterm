# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Maybe create a small console program which allows us to:
     - send packets directly
     - receive them directly
     - see the binary data of the packet
     - see the representation of the packet
     - ability for incoming and outgoing
"""
from ecrterm import common, conv
from ecrterm.packets import *
from ecrterm import transmission
from ecrterm.transmission.signals import *
import time, sys, logging
from ecrterm.common import TERMINAL_STATUS_CODES

class A(object):
    def write(self, *args, **kwargs):
        pass
_logfile = A()

def dismantle_serial_packet(data):
    apdu = []
    crc = None
    i = 2
    header = data[:i]
    #header = conv.bs2hl(header)
    # test if there was a transmission:
    if header == []:
        raise common.TransportLayerException, 'No Header'
    # test our header to be valid
    if header != [DLE, STX]:
        raise common.TransportLayerException, "Header Error: %s" % header
    # read until DLE, ETX is reached.
    dle = False
    while not crc and i < len(data):
        b = data[i] # read a byte.
        if b == ETX and dle:
            # dle was set, and this is ETX, so we are at the end.
            # we read the CRC now.
            crc = [data[i + 1], data[i + 2]]
            # and break
            continue
        elif b == DLE:
            if not dle:
                # this is a dle
                dle = True
                continue
            else:
                # this is the second dle. we take it.
                dle = False
        elif dle:
            # dle was set, but we got no etx here.
            # this seems to be an error.
            raise Exception, "DLE without sense detected."
        # we add this byte to our apdu.
        apdu += [b]
        i += 1
    return crc, apdu

def parse_represented_data(data):
    # represented data
    if isinstance(data, basestring):
        # we assume a bytelist like 10 02 03.... 
        data = conv.toBytes(data)
    # first of all, serial data starts with 10 02, so everything
    # starting with 10 will be assumed as "serial packet" and first "demantled"
    if data[0] == DLE:
        try:
            crc, data = dismantle_serial_packet(data)
        except common.TransportLayerException:
            pass
    elif data[0] == ACK:
        if len(data) == 1:
            return 'ACK'
    elif data[0] == NAK:
        if len(data) == 1:
            return 'NAK'
    # then we create the packet and return that.
    p = Packet.parse(data)
    return p

def ecr_log(data, incoming=False):
    try:
        if incoming:
            incoming = '<'
        else:
            incoming = '>'
        if isinstance(data, basestring):
            data = conv.bs2hl(data)
        # logit to the logfile
        try:
            _logfile.write('%s %s\n' % (incoming, conv.toHexString(data)))
        except:
            pass
        try:
            data = repr(parse_represented_data(data))
            _logfile.write('= %s\n' % data)
        except Exception, e:
            print "DEBUG: Cannot be represented: %s" % data
            print e
            _logfile.write('? did not understand ?\n')
            data = conv.toHexString(data)
        print "%s %s" % (incoming, data)
    except:
        import traceback
        traceback.print_exc()
        print "| error in log"

class ECR(object):
    transmitter = None
    transport = None
    version = None
    terminal_id = None
    MAX_TEXT_LINES = 4
    _state_registered = None
    _state_connected = None

    def __get_last(self):
        if self.transmitter is not None:
            return self.transmitter.last
    #!: Last is a short access for transmitter.last if possible.
    last = property(__get_last)

    def __init__(self, device='/dev/ttyUSB0'):
        """
            Initializes an ECR object and connects to the serial device given
            Fails if Serial Device is not found.
            
            You can access the Device on low level as the `transport`
            You can access the Protocol Handler on low level as `transmission`
        """
        self.transport = transmission.SerialTransport(device)
        #self.transport.slog = ecr_log
        self.daylog = []
        self.daylog_template = ''
        self.history = []
        self.terminal_id = None
        # we save some states here.
        self._state_registered = False
        self._state_connected = False

        if self.transport.connect():
            self.transmitter = transmission.Transmission(self.transport)
            self._state_connected = True
        else:
            raise Exception, "ECR could not connect."

    def register(self):
        """
            registers this ECR at the PT, locking menus
            for real world conditions.
        """
        ret = self.transmit(Registration())
        
        if ret == TRANSMIT_OK:
            # get the terminal-id if its there.
            for inc, packet in self.transmitter.last_history:
                if inc and isinstance(packet, Completion):
                    if 'tid' in packet.bitmaps_as_dict().keys():
                        self.terminal_id = packet.bitmaps_as_dict()\
                                            .get('tid', BCD(0)).value()
            # remember this.
            self._state_registered = True
        return ret


    def register_unlocked(self):
        """
            registers to the PT, not locking the master menu on it.
            do not use in production environment.
        """
        ret = self.transmit(
                    Registration(
                        config_byte=Registration.generate_config(
                            ecr_controls_admin=False),))
        if ret == TRANSMIT_OK:
            self._state_registered = True
        return ret
    
    def _end_of_day_info_packet(self, history=None):
        '''
            search for an end of day packet status information in the last packets
            can also search in any history list.
        '''
        # helper function to scan for end of day information via packets.
        status_info = None
        plist = history or self.transmitter.last_history
        for inc, packet in plist:
            if inc: # incoming
                if isinstance(packet, StatusInformation):
                    status_info = packet
        if status_info:
            eod_info = status_info.get_end_of_day_information()
            # we add terminal id to it.
            eod_info['terminal-id'] = self.terminal_id
            return eod_info


    def end_of_day(self):
        """
            - sends an end of day packet.
            - saves the log in `daylog`
            
            @returns: 0 if there were no protocol errors.
        """
        #old_histoire = self.transmitter.history
        #self.transmitter.history = []
        # we send the packet
        result = self.transmit(EndOfDay())
        # now save the log
        self.daylog = self.last_printout()
        
        if not self.daylog:
            # there seems to be no printout. we search in statusinformation.
            eod_info = self._end_of_day_info_packet()
            try:
                self.daylog = (self.daylog_template % eod_info).split('\n')
            except:
                import traceback
                traceback.print_exc()
                logging.error('Error in Daylog Template')
        return result

    def last_printout(self):
        """
            returns all printlines from the last history.
            @todo: TextBlock support - if some printer decides to do it that way.
        """
        printout = []
        for entry in self.transmitter.last_history:
            inc, packet = entry
            #old_histoire += [(inc, packet)]
            if inc and isinstance(packet, PrintLine):
                printout += [ packet.fixed_values['text'] ]
        return printout

    def payment(self, amount_cent=50):
        """
            executes a payment in amount of cents.
            @returns: True, if payment went through, or False if it was
            canceled. 
            throws exceptions.
        """
        pkg = Authorisation(
                    amount=amount_cent, # in cents.
                    currency_code=978, #euro, only one that works, can be skipped.
                    )
        code = self.transmit(pkg)

        if code == 0:
            # now check if the packet actually got what it wanted.
            if self.transmitter.last.completion:
                if isinstance(self.transmitter.last.completion, Completion):
                    return True
            else:
                return False
        else:
            # @todo: remove this.
            print "transmit error?"
        return False

    def restart(self):
        """
            restarts/resets the PT.
        """
        self._state_registered = False
        return self.transmit(ResetTerminal())

    def reset(self):
        """
            - resets transport: @see ecrterm.transmission.Transport.reset()
            - restarts pt: @see self.restart()
        """
        self.transport.reset()
        time.sleep(1)
        ret = self.restart()
        time.sleep(1)
        return ret

    def show_text(self,
                  lines=['Hello world!', ],
                  duration=5,
                  beeps=0):
        """
            displays a text on the PT screen for duration of seconds.
            
            @param lines: a list of strings.
            @param duration: 0 for forever.
            @param beeps: make some noise.
            
            @note: any error due to wrong strings given are not checked.
        """
        kw = {'display_duration': duration}
        if beeps:
            kw['beeps'] = int(beeps)
        i = 1
        for line in lines[:self.MAX_TEXT_LINES]:
            kw['line%s' % i] = line
            i += 1
        return self.transmit(ShowText(**kw))

    def status(self):
        """
            executes a status enquiry. also sets self.version if not set.
            success:
            returns 0 if successful, and status is unchanged.
            returns an int status code if status has changed.
            errors:
            returns None if no status was transmitted.
            returns False on transmit errors.
            
            to check for the status code:
                common.TERMINAL_STATUS_CODES.get( status, 'Unknown' )
        """
        errors = self.transmit(StatusEnquiry())
        if not errors:
            if isinstance(self.last.completion, Completion):
                # try to get version
                if not self.version:
                    self.version = self.last.completion.fixed_values.get('sw-version', None)
                return self.last.completion.fixed_values.get('terminal-status', None)
            # no completion means some error.
        return False


    def transmit(self, packet):
        """
            transmits a packet, therefore introducing the protocol cascade.
            rewrite this function if you want packets be routed anywhere
            since the whole ECR Object uses this function to transmit.
            
            use `last` property to access last packet transmitted.
        """
        # we actually make a small sleep, allowing better flow.
        time.sleep(0.2)
        transmission = self.transmitter.transmit(packet)
        return transmission

    # dev functions.
    #########################################################################

    def wait_for_status(self):
        """
            waits until self.status() returns 0 (or False/None)
            polls the PT in 2 second intervals.
            this function prints out the status string. 
            use it as code example.
        """
        status = self.status()
        while status:
            print TERMINAL_STATUS_CODES.get(status, 'Unknown Status')
            time.sleep(2)
            status = self.status()

    def listen(self, timeout=15):
        """
            dev function to simply listen.
        """
        ok, message = None, None
        while True:
            try:
                ok, message = self.transport.receive(timeout)
                if ok and message:
                    return message
            except Exception, e:
                print e
                continue
            print "-mark-"

    def devprint_packets(self):
        """
            dev function to execute the script located in base_packets
            useful to get a list of all parsed packets.
        """
        from pprint import pprint
        pprint(Packets.packets)

    def devprint_bitmaps(self):
        """
            dev function to execute the script located in bitmaps
            useful to get a list of all valid bitmaps.
        """
        from pprint import pprint
        from ecrterm.packets.bitmaps import BITMAPS_ARGS
        pprint(BITMAPS_ARGS)

    def detect_pt(self):
        # note: this only executes utils.detect_pt with the local ecrterm.
        from ecrterm.utils import detect_pt
        result = detect_pt(silent=True, ecr=self, timeout=2)
        self.transport.connect()
        return result

    def parse_str(self, s):
        return parse_represented_data(s)

if __name__ == '__main__':
    _logfile = open('./terminallog.txt', 'aw')
    _logfile.write('-MARK-\n')
    e = ECR()
    #e.end_of_day()
    e.show_text(['Hello world!', 'Testing', 'myself.'], 5, 0)
    print "preparing for payment."
    e.get_ready()
    print e.payment(50)
