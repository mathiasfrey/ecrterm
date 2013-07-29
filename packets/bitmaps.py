# -*- coding: utf-8 -*-
"""
    Implements all known Bitmaps in two Dictionaries:
    
    BITMAPS is keyed after the CODE of the bitmap in the protocol.
    use this if you know "the code" of the bitmap and retrieve its class,
    keyname (and description)
    
    BITMAPS_ARGS is created from BITMAPS, representing bitmaps in a 
    key-value-store. use this if you know "the key name" of the bitmap
    and want to get its class, code (and description)
"""
from ecrterm.packets.bmp import BMP

BITMAPS = {
    0x01 : (BMP.FormatByte(1), 'timeout', "binary time-out"),
    0x02 : (BMP.FormatByte(1), 'max_status_infos', "binary max.status infos"),
    0x03 : (BMP.FormatByte(1), 'service_byte', "binary service-byte"),
    0x04 : (BMP.FormatBCDByte(6), 'amount', "Amount"),
    0x05 : (BMP.FormatByte(1), 'pump_nr', "binary pump-Nr."),
    0x06 : (BMP.FormatTLV(), 'tlv', "TLV"),
    0x0B : (BMP.FormatBCDByte(3), 'trace_number', "trace-number"),
    0x0C : (BMP.FormatBCDByte(3), 'time', "Time"),
    0x0D : (BMP.FormatBCDByte(2), 'date_day', "date, MM DD (see AA)"),
    0x0E : (BMP.FormatBCDByte(2), 'card_expire', "expiry-date, YY MM"),
    0x17 : (BMP.FormatBCDByte(2), 'card_sequence_number', "card sequence-number"),
    0x19 : (BMP.FormatByte(1), 'type', "binary status-byte/payment-type/card-type"),
    0x22 : (BMP.FormatLLVAR(), 'card_number', "card_number, PAN / EF_ID, 'E' used to indicate masked numeric digit"),
    0x23 : (BMP.FormatLLVAR(), 'track_2', "track 2 data, 'E' used to indicate masked numeric digit1"),
    0x24 : (BMP.FormatLLLVAR(), 'track_3', "track 3 data, 'E' used to indicate masked numeric digit1"),
    0x27 : (BMP.FormatByte(1), 'result_code', "binary result-code"),
    0x29 : (BMP.FormatBCDByte(4), 'tid', "TID"),
    0x2A : (BMP.FormatByte(15), 'vu', "ASCII VU-number"),
    0x2D : (BMP.FormatLLVAR(), 'track_1', "track 1 data"),
    0x2E : (BMP.FormatLLLVAR(), 'sync_chip_data', "sychronous chip data"),
    0x37 : (BMP.FormatBCDByte(3), 'trace_number_original', "trace-number of the original transaction for reversal"),
    0x3A:  (BMP.FormatBCDByte(2), 'cvv', 'the field cvv is optionally used for mail order'),
    0x3B : (BMP.FormatByte(8), 'aid', "AID authorisation-attribute"),
    0x3C : (BMP.FormatLLLVAR(), 'additional', "additional-data/additional-text"),
    0x3D : (BMP.FormatBCDByte(3), 'password', "Password"),
    0x49 : (BMP.FormatBCDByte(2), 'currency_code', "currency code"),
    0x60 : (BMP.FormatLLLVAR(), 'totals', "individual totals"),
    0x87 : (BMP.FormatBCDByte(2), 'receipt', "receipt-number"),
    0x88 : (BMP.FormatBCDByte(3), 'turnover', "turnover record number"),
    0x8A : (BMP.FormatByte(1), 'card_type', "binary card-type (card-number according to ZVT-protocol; comparison 8C)"),
    0x8B : (BMP.FormatLLVAR(), 'card_name', "card-name"),
    0x8C : (BMP.FormatByte(1), 'card_operator', "binary card-type-ID of the network operator (comparison 8A)"),
    0x92 : (BMP.FormatLLLVAR(), 'offline_chip', "additional-data ec-Cash with chip offline"),
    0x9A : (BMP.FormatLLLVAR(), 'geldkarte', "Geldkarte payments-/ failed-payment record/total record Geldkarte"),
    0xA0 : (BMP.FormatByte(1), 'result_code_as', "binary result-code-AS"),
    0xA7 : (BMP.FormatLLVAR(), 'chip_ef_id', "chip-data, EF_ID"),
    0xAA : (BMP.FormatBCDByte(3), 'date', "date YY MM DD (see 0D)"),
    0xAF : (BMP.FormatLLLVAR(), 'ef_info', "EF_Info"),
    0xBA : (BMP.FormatByte(5), 'aid_param', "binary AID-parameter"),
    0xD0 : (BMP.FormatByte(1), 'algo_key', "binary algorithm-Key"),
    0xD1 : (BMP.FormatLLVAR(), 'offset', "card offset/PIN-data"),
    0xD2 : (BMP.FormatByte(1), 'direction', "binary direction"),
    0xD3 : (BMP.FormatByte(1), 'key_position', "binary key-position"),
    0xE0 : (BMP.FormatByte(1), 'input_min', "binary min. length of the input"),
    0xE1 : (BMP.FormatLLVAR(), 'iline1', "text2 line 1"),
    0xE2 : (BMP.FormatLLVAR(), 'iline2', "text2 line 2"),
    0xE3 : (BMP.FormatLLVAR(), 'iline3', "text2 line 3"),
    0xE4 : (BMP.FormatLLVAR(), 'iline4', "text2 line 4"),
    0xE5 : (BMP.FormatLLVAR(), 'iline5', "text2 line 5"),
    0xE6 : (BMP.FormatLLVAR(), 'iline6', "text2 line 6"),
    0xE7 : (BMP.FormatLLVAR(), 'iline7', "text2 line 7"),
    0xE8 : (BMP.FormatLLVAR(), 'iline8', "text2 line 8"),
    0xE9 : (BMP.FormatByte(1), 'max_input_length', "binary max. length of the input"),
    0xEA : (BMP.FormatByte(1), 'input_echo', "binary echo the Input"),
    0xEB : (BMP.FormatByte(8), 'mac', "binary MAC over text 1 and text 2"),
    0xF0 : (BMP.FormatByte(1), 'display_duration', "binary display-duration"),
    0xF1 : (BMP.FormatLLVAR(), 'line1', "text1 line 1"),
    0xF2 : (BMP.FormatLLVAR(), 'line2', "text1 line 2"),
    0xF3 : (BMP.FormatLLVAR(), 'line3', "text1 line 3"),
    0xF4 : (BMP.FormatLLVAR(), 'line4', "text1 line 4"),
    0xF5 : (BMP.FormatLLVAR(), 'line5', "text1 line 5"),
    0xF6 : (BMP.FormatLLVAR(), 'line6', "text1 line 6"),
    0xF7 : (BMP.FormatLLVAR(), 'line7', "text1 line 7"),
    0xF8 : (BMP.FormatLLVAR(), 'line8', "text1 line 8"),
    0xF9 : (BMP.FormatByte(1), 'beeps', "binary number of beep-tones"),
    0xFA : (BMP.FormatByte(1), 'status', "binary status"),
    0xFB : (BMP.FormatByte(1), 'ok_required', "binary confirmation the input with <OK> required"),
    0xFC : (BMP.FormatByte(1), 'dialog_control', "binary dialog-control"),
}

BITMAPS_ARGS = {}
test_keys = []
for key in BITMAPS.keys():
    klass, k, info = BITMAPS[key]
    test_keys += [k]
    BITMAPS_ARGS[k] = (key, klass, info)

if __name__ == '__main__':
    from pprint import pprint
    pprint(BITMAPS_ARGS)
    if len(test_keys) != len(set(test_keys)):
        print "#" * 80
        raise Exception, "Duplicate Keys in BITMAPS_ARGS, please check."
