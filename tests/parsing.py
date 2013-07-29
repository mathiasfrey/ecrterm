# -*- coding: utf-8 -*-<
"""
    Incoming Packets should be always parsable.
    this test tries to look at the parser in detail.
"""
import unittest
import sys
import logging
#sys.path.insert(0, '..')

from ecrterm.packets.bmp import *
from ecrterm.ecr import parse_represented_data
from ecrterm.packets import *
from ecrterm import conv

class TestParsingMechanisms(unittest.TestCase):

    def setUp(self):
        pass

    def test_all_packets(self):
        """
            create packets, dump their binary data and try to find them
            out again!
        """
        PACKETS = Packets.packets.values()
        for packet in PACKETS:
            rep = parse_represented_data(conv.toHexString(packet().to_list()))
            self.assertEqual(rep.__class__,
                                 packet)

    def test_version_completion(self):
        # following completion is sent by the PT with version on statusenquiry:
        data_expected = """10 02 06 0F 0B F0 F0 F7 32 2E 31 34 2E 31 35 00 10 03 B1 11"""
        # small test to test the completion with software version to be recognized.
        rep = parse_represented_data(data_expected)
        self.assertEqual(rep.__class__, Completion)


    def test_parsing_two(self):
        """
            parse some packets 
             - from the tutorial 
             - from complicated scenarios
             - from failing parsings
            and tell me if they are understood:
        """
        PACKETS = [
            # 06 D1
            '10 02 06 D1 17 00 20 20 20 20 20 20 20 20 20 4B 61 73 73 65 6E 73 63 68 6E 69 74 74 10 03 2F 07',
            # 04 0F
            '10 02 04 0F 37 27 00 04 00 00 00 00 40 00 49 09 78 0C 09 38 48 0D 04 25 22 F1 F1 59 66 66 66 66'\
            'D2 00 21 22 01 00 17 00 01 87 01 75 0B 61 39 95 19 40 29 60 09 99 14 0E 05 12 8A 02 10 03 90 8C',
                   ]
        i = 0
        for packet in PACKETS:
            rep = parse_represented_data(packet)
            logging.info(rep)
            if not isinstance(rep, Packet):
                raise AssertionError, "Packet could not be parsed: #%s" % i
            i += 1

if __name__ == '__main__':
    unittest.main()
