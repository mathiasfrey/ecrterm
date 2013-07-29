# -*- coding: utf-8 -*-
TIMEOUT_T1 = 0.2
TIMEOUT_T2 = 15
TIMEOUT_T4 = 180
TIMEOUT_T4_DEFAULT = 180 # sec
TIMEOUT_T3 = 5 # sec

#: command separator
DLE = 0x10
#: start transmission
STX = 0x02
#: end transission
ETX = 0x03
#: ACK
ACK = 0x06
#: NAK
NAK = 0x15
#: carriage return
CR = 0x0d
#: linefeed
LF = 0x0a

# Transmission signals.
TRANSMIT_OK = 0
TRANSMIT_ABORT = 1
TRANSMIT_ERROR = 2
TRANSMIT_TIMEOUT = 3
