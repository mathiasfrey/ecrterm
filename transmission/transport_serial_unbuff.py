# -*- coding: utf-8 -*-
from ecrterm.transmission.transport_serial import *
import serial #@UnresolvedImport

class SerialTransportUnbuffered(SerialTransport):
    class UnbufferedSerial(serial.Serial):
        """ override Serial.read to use the *unbuffered* read function """
        def read(self, size=1, timeout=None):
            """Read size bytes from the serial port. If a timeout is set it may
               return less characters as requested. With no timeout it will block
               until the requested number of bytes is read."""
            if self.fd is None: raise serial.portNotOpenError
            read = []
            nread = 0
            fd = self.fd
            fds = [fd]
            # timeout in seconds
            if timeout is None and self._timeout:
                timeout = self._timeout
            if size > 0:
                while nread < size:
                    #print "\tread(): size",size, "have", len(read)    #debug
                    ready, _, _ = select.select(fds, [], [], timeout)
                    if not ready:
                        break   #timeout
                    buf = os.read(fd, size - nread)
                    if not buf:
                        break  #early abort on timeout or error
                    read.append(buf)
                    nread += len(buf)
            return ''.join(read)
    SerialCls = UnbufferedSerial
