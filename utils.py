# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Utility Functions.
    
    @author g4b
"""
from ecrterm.ecr import ECR
from ecrterm import packets

def detect_pt(device='/dev/ttyUSB0', timeout=2, silent=True,
              ecr=None):
    """ connects to given serial port and tests if a PT is present.
        if present: tries to return version number or True
        returns False otherwise.
        
        @param timeout: set the timeout to have a faster response time.
        @param silent: if False, exceptions won't be caught, default: True.
        @param ecr: give a working ecr to perform this task. note: you have to
            reconnect the transport since the timeout is changed.
    """
    def __detect_pt(port, timeout, ecr):
        e = ecr or ECR(port)
        # reconnect to have lower timeout
        e.transport.connect(timeout=timeout)
        errors = e.transmit(packets.StatusEnquiry())
        if not errors:
            if isinstance(e.last.completion, packets.Completion):
                return e.last.completion.fixed_values.get('sw-version', True) or True
            return True
        return False
    if silent:
        try:
            return __detect_pt(device, timeout, ecr)
        except:
            return False
    else:
        return __detect_pt(device, timeout, ecr)

if __name__ == '__main__':
    if detect_pt():
        print "PT is online at ttyUSB0"
    else:
        print "PT cant be found at ttyUSB0"

