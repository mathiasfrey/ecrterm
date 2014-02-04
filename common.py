# -*- coding: utf-8 -*-
"""
    Common Base classes, Definitions and Ancestors.
"""

INTERMEDIATE_STATUS_CODES = {
 0x00: 'PT is waiting for amount - confirmation',
 0x01: 'please watch PIN - Pad',
 0x02: 'please watch PIN - Pads',
 0x03: 'not accepted',
 0x04: 'PT is waiting for response from FEP',
 0x05: 'PT is sending auto - reversal',
 0x06: 'PT is sending post - bookings',
 0x07: 'card not admitted',
 0x08: 'card unknown / undefined',
 0x09: 'expired card',
 0x0A: 'insert card',
 0x0B: 'please remove card !',
 0x0C: 'card not readable',
 0x0D: 'processing error',
 0x0E: 'please wait...',
 0x0F: 'PT is commencing an automatic end - of - day batch',
 0x10: 'invalid card',
 0x11: 'balance display',
 0x12: 'system malfunction',
 0x13: 'payment not possible',
 0x14: 'credit not sufficient',
 0x15: 'incorrect PIN',
 0x16: 'limit not sufficient',
 0x17: 'please wait...',
 0x18: 'PIN try limit exceeded',
 0x19: 'card - data incorrect',
 0x1A: 'service - mode',
 0x1B: 'approved. please fill - up',
 0x1C: 'approved. please take goods',
 0x1D: 'declined',
 0x26: 'PT is waiting for input of the mobile - number',
 0x27: 'PT is waiting for repeat of mobile number',
 0x41: 'please watch PIN - Pad please remove card !',
 0x42: 'please watch PIN - Pad please remove card !',
 0x43: 'not accepted, please remove card !',
 0x44: 'PT is waiting for response from FEP  please remove card !',
 0x45: 'PT is sending auto - reversal  please remove card !',
 0x46: 'PT is sending post - booking  please remove card !',
 0x47: 'card not admitted  please remove card !',
 0x48: 'card unknown / undefined  please remove card !',
 0x49: 'expired card please remove card !',
 0x4A: '',
 0x4B: 'please remove card !',
 0x4C: 'card not readable  please remove card !',
 0x4D: 'processing error please remove card !',
 0x4E: 'please wait... please remove card !',
 0x4F: 'PT is commencing an automatic end - of - day batch please remove card !',
 0x50: 'invalid card please remove card !',
 0x51: 'balance display  please remove card !',
 0x52: 'system malfunction please remove card !',
 0x53: 'payment not possible  please remove card !',
 0x54: 'credit not sufficient please remove card !',
 0x55: 'incorrect PIN please remove card !',
 0x56: 'limit not sufficient  please remove card !',
 0x57: 'please wait...  please remove card !',
 0x58: 'PIN try limit exceeded please remove card !',
 0x59: 'card - data incorrect please remove card !',
 0x5A: 'service - mode  please remove card !',
 0x5B: 'approved. please fill - up  please remove card !',
 0x5C: 'approved. please take goods  please remove card !',
 0x5D: 'declined please remove card !',
 0x66: 'PT is waiting for input of the mobil - number please remove card !',
 0x67: 'PT is waiting for repeat of the mobil - number please remove card !',
 0xC7: 'PT is waiting for input of the mileage',
 0xC8: 'PT is waiting for cashier',
 0xC9: 'PT is commencing an automatic diagnosis',
 0xCA: 'PT is commencing an automatic initialisation',
 0xCB: 'merchant - journal full',
 0xCC: 'debit advice not possible, PIN required',
 0xD2: 'connecting dial - up',
 0xD3: 'dial - up connection made',
 0xE0: 'PT is waiting for application - selection',
 0xE1: 'PT is waiting for language - selection',
 0xF1: 'offline',
 0xF2: 'online',
 0xF3: 'offline transaction',
 0xFF: 'custom or unknown status.',
}

ERRORCODES = {
# ERRORCODES PAGE: 165
# SUBSTITUTED: ^[A-Fa-f\d]{2,2} 
# TO: 0x\0: "
# AND: .*$ TO: \0",
0x00 : "00 no error",
# 01-63 01 – 99 errorcodes from network-operator system/authorisation-system",
0x64: "card not readable (LRC-/parity-error)",
0x65: "card-data not present (neither track-data nor chip found)",
0x66: "processing-error (also for problems with card-reader mechanism)",
0x67: "function not permitted for ec- and Maestro-cards",
0x68: "function not permitted for credit- and tank-cards",
0x6A: "turnover-file full",
0x6B: "function deactivated (PT not registered)",
0x6C: "abort via time-out or abort-key ",
0x6E: "card in blocked-list (response to command 06 E4)",
0x6F: "wrong currency",
0x71: "credit not sufficient (chip-card)",
0x72: "chip error ",
0x73: "card-data incorrect (e.g. country-key check, checksum-error)",
0x77: "end-of-day batch not possible ",
0x78: "card expired",
0x79: "card not yet valid",
0x7A: "card unknown",
0x7D: "communication error (communication module does not answer or is not present)",
0x83: "function not possible",
0x85: "key missing",
0x89: "PIN-pad defective",
0x9A: "trnasferprotocol- error",
0x9B: "error from dial-up/communication fault",
0x9C: "please wait",
0xA0: "receiver not ready",
0xA1: "remote station does not respond",
0xA3: "no connection",
0xA4: "submission of Geldkarte not possible",
0xB1: "memory full",
0xB2: "merchant-journal full",
0xB4: "already reversed",
0xB5: "reversal not possible",
0xB7: "pre-authorisation incorrect (amount too high) or amount wrong",
0xB8: "error pre-authorisation",
0xBF: "voltage supply to low (external power supply)",
0xC0: "card locking mechanism defective",
0xC1: "merchant-card locked ",
0xC2: "diagnosis required",
0xC3: "maximum amount exceeded",
0xC4: "card-profile invalid. New card-profiles must be loaded.",
0xC5: "payment method not supported",
# PAGE 166
0xC6 : "currency not applicable",
0xC8 : "amount zu small",
0xC9 : "max. transaction-amount zu small",
0xCB : "function only allowed in EURO",
0xCC : "printer not ready",
0xD2 : "function not permitted for service-cards/bank-customer-cards",
0xDC : "card inserted",
0xDD : "error during card-eject (for motor-insertion reader)",
0xDE : "error during card-insertion (for motor-insertion reader)",
0xE0 : "remote-maintenance activated",
0xE2 : "card-reader does not answer / card-reader defective",
0xE3 : "shutter closed",
0xE7 : "min. one goods-group not found",
0xE8 : "no  goods-groups-table loaded",
0xE9 : "restriction-code not permitted",
0xEA : "card-code not permitted (e.g. card not activated via Diagnosis)",
0xEB : "function not executable (PIN-algorithm unknown)",
0xEC : "PIN-processing not possible",
0xED : "PIN-pad defective",
0xF0 : "open end-of-day batch present",
0xF1 : "ec-cash/Maestro offline error",
0xF5 : "OPT-error",
0xF6 : "OPT-data not available (= OPT personalisation required)",
0xFA : "error transmitting offline-transactions (clearing error)",
0xFB : "turnover data-set defective",
0xFC : "necessary device not present or defective",
0xFD : "baudrate not supported",
0xFE : "register unknown",
0xFF : "system error" # (= other/unknown error), See TLV tags 1F16 and 1F17
}

TERMINAL_STATUS_CODES = {
0x00 : "PT ready",
0x51 : "initialisation required",
0x62 : "date/time incorrect",
0x9C : "please wait (e.g. software-update still running)",
0xB1 : "memory full",
0xB2 : "merchant-journal full",
0xBF : "voltage supply too low  (external power supply)",
0xC0 : "card locking mechanism defect",
0xC1 : "merchant card locked",
0xC2 : "diagnosis required",
0xC4 : "card-profile invalid. New card-profiles must be loaded",
0xCC : "printer not ready",
0xDC : "card inserted",
0xDF : "out-of-order",
0xE0 : "remote-maintenance activated",
0xE1 : "card not completely removed",
0xE2 : "card-reader doe not answer / card-reader defective",
0xE3 : "shutter closed",
0xF6 : "OPT-data not availble (= OPT-Personalisation required)" }

"""
DEBUG_PACKET_NAME = {
[0x0F, None]: "RFU for proprietary applications, the utilisation for particular cases should be clarified between manufacturers",
[0x01, 0x01]: "RFU",
[0x04, 0x01]: "Set Date and Time in ECR",
[0x04, 0x0E]: "Menu-Request",
[0x04, 0x0F]: "Status-Information",
[0x04, 0xFF]: "Intermediate-Statusinformation",
[0x05, 0x01]: "Status-Enquiry",
[0x05, 0xFF]: "RFU",
[0x06, 0x00]: "Registration",
[0x06, 0x01]: "Authorisation",
[0x06, 0x02]: "Log-Off",
[0x06, 0x03]: "Account Balance Request",
[0x06, 0x09]: "Prepaid Top-Up",
[0x06, 0x0A]: "Tax Free",
[0x06, 0x0B]: "RFU",
[0x06, 0x0C]: "TIP",
[0x06, 0x0F]: "Completion",
[0x06, 0x10]: "Send Turnover Totals",
[0x06, 0x11]: "RFU",
[0x06, 0x12]: "Print Turnover Receipts",
[0x06, 0x18]: "Reset Terminal",
[0x06, 0x1A]: "Print System Configuration",
[0x06, 0x1B]: "Set/Reset Terminal-ID",
[0x06, 0x1E]: "Abort",
[0x06, 0x20]: "Repeat Receipt",
[0x06, 0x21]: "Telephonic Authorisation",
[0x06, 0x22]: "Pre-Authorisation/Reservation",
[0x06, 0x23]: "Partial-Reversal of a Pre-Authorisation/Booking of a Reservation",
[0x06, 0x24]: "Book Total",
[0x06, 0x25]: "Pre-Authorisation Reversal",
[0x06, 0x30]: "Reversal",
[0x06, 0x31]: "Refund",
[0x06, 0x50]: "End-of-Day",
[0x06, 0x51]: "Send offline Transactions",
[0x06, 0x70]: "Diagnosis",
[0x06, 0x79]: "Selftest",
[0x06, 0x82]: "RFU",
[0x06, 0x85]: "Display Text (only included for downwards-compatibility, for new implementations use 06 E0)",
[0x06, 0x86]: "Display Text with Numerical Input (only included for downwards-compatibility, for new implementations use 06 E2)",
[0x06, 0x87]: "PIN-Verification for Customer-Card (only included for downwards-compatibility, for new implementations use 06 E3)",
[0x06, 0x88]: "Display Text with Function-Key Input (only included for downwards-compatibility, for new implementations use 06 E1)",
[0x06, 0x90]: "RFU",
[0x06, 0x91]: "Set Date and Time in PT",
[0x06, 0x93]: "Initialisation",
[0x06, 0x95]: "Change Password",
[0x06, 0xB0]: "Abort",
[0x06, 0xC0]: "Read Card",
[0x06, 0xCE]: "RFU",
[0x06, 0xD1]: "Print Line",
[0x06, 0xD3]: "Print Text-Block",
[0x06, 0xD4]: "RFU",
[0x06, 0xD8]: "Dial-Up",
[0x06, 0xD9]: "Transmit Data via Dial-Up",
[0x06, 0xDA]: "Receive Data via Dial-Up ",
[0x06, 0xDB]: "Hang-Up",
[0x06, 0xDD]: "Transparent-Mode",
[0x06, 0xE0]: "Display Text",
[0x06, 0xE1]: "Display Text with Function-Key Input",
[0x06, 0xE2]: "Display Text with Numerical Input",
[0x06, 0xE3]: "PIN-Verification for Customer-Card",
[0x06, 0xE4]: "Blocked-List Query to ECR",
[0x08, 0x01]: "Activate Service-Mode",
[0x08, 0x02]: "Switch Protocol",
[0x08, 0x10]: "Software-Update",
[0x08, 0x11]: "Read File",
[0x08, 0x12]: "Delete File",
[0x08, 0x20]: "Start OPT Action",
[0x08, 0x21]: "Set OPT Point-in-Time",
[0x08, 0x22]: "OPT-Pre-Initialisation",
[0x08, 0x23]: "Output OPT-Data",
[0x08, 0x24]: "OPT Out-of-Order",
[0x08, 0x30]: "Select Language",
[0x08, 0x40]: "Change Baudrate",
[0x08, 0x50]: "Activate Card-Reader",
[0x0F, None]: "reserved for proprietary extensions ",
[0x80, 0x00]: "Positive Acknowledgement",
[0x84, 0x00]: "Positive Acknowledgement",
[0x84, None]: "Negative Acknowledgement",
[0x84, 0x9C]: "Repeat Statusinfo"
}
"""

class Logling(object):
    """
        a simple log interface
    """
    def log(self, *args, **kwargs):
        print " ".join(args)

class Dumpling(object):
    """
        Interface, which defines that this object can
          - dump itself into a list of bytes
          - tell you how much bytes of data it has.
          - dumpling does not solve how you store your data.
    """
    def dump(self):
        """
            returns a list of bytes, representing this dumpling in the stream.
        """
        return []

    def dump_length(self):
        """
            has to return how many bytes this class does dump.
            returns an integer.
        """
        return len(self.dump())

class Transport(Logling):
    def connect(self, *args, **kwargs):
        """
            connect to transport.
        """
        pass
    def receive(self, timeout=None, *args, **kwargs):
        """
            receive data.
        """
        pass
    def send(self, message, *args, **kwargs):
        """
            send data.
        """
        pass

class ZVTException(Exception):
    pass

class TransportLayerException(ZVTException):
    pass

class TransportTimeoutException(TransportLayerException):
    pass

class ApplicationLayerException(ZVTException):
    pass
