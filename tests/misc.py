# -*- coding: utf-8 -*-
"""
    Misc. Tests.
    
    @author g4b
"""
import unittest
#import sys
#sys.path.insert(0, '..')

from ecrterm.packets.bmp import *

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        pass

    def test_bcd(self):
        """ small test for bcds """
        n1, n2 = 4, 5
        bcd_n = 0x45
        # bcd_split should create two numbers out of bcd.
        self.assertEqual(BCD.bcd_split(bcd_n), (n1, n2))
        # bcd unite however should create one bcd byte out of two numbers
        self.assertEqual(BCD.bcd_unite((n1, n2)), bcd_n)

        # now test the full ones
        password = '123456'
        bcd_pass = [ 0x12, 0x34, 0x56 ]
        password_nums = [ int(x) for x in password ]
        self.assertEqual(BCD.encode_bcd(password),
                         bcd_pass)
        self.assertEqual(BCD.decode_bcd(bcd_pass),
                         password_nums)
        # test instantiation:
        b = BCD(password)
        b._length = 3
        #print b.values()
        self.assertEqual(b.value(), password)
        # test dumping
        b = BCD(1)
        b._length = 3
        b._id = 666 # this is actually impossible, but manually valid.
        d = b.dump()
        self.assertEqual(d,
                         [666, 00, 00, 01])


    def test_bmp(self):
        """
            test if the classmethods in bmp work
        """
        bignum = 4321056789
        fcd_seq = [ 0xf4, 0xf3, 0xf2, 0xf1, 0xf0,
              0xf5, 0xf6, 0xf7, 0xf8, 0xf9]
        self.assertEqual(
            BCD.encode_fcd(bignum),
            fcd_seq)
        self.assertEqual(
            BCD.decode_fcd(fcd_seq),
            bignum)

    def test_llvar(self):
        pass

if __name__ == '__main__':
    unittest.main()
