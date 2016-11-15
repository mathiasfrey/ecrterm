# -*- coding: utf-8 -*-
"""
    Transmission.
    
    You could say, this is the application layer of the ZVT Protocol
    
    Transmission regulates the packetflow and the rules where the packets go.
    
    It uses a Transport (SerialTransport) to send its data, and you feed
    it with a packet through the transmit() method. All further communication
    is done in the packets.
    
    @author g4b
"""

from ecrterm.transmission._transmission import *
from ecrterm.transmission import signals, zvt
from ecrterm.transmission.transport_serial import SerialTransport
