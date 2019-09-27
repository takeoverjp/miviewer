#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from miviewer import parse_meminfo_line, parse_meminfo

TEST_MEMINFO="""\
MemTotal:       32802752 kB
MemFree:        28315612 kB
MemAvailable:   29904600 kB
Buffers:          551604 kB
Cached:          1700912 kB
SwapCached:            0 kB
Active:          2798744 kB
Inactive:         827776 kB
Active(anon):    1673760 kB
Inactive(anon):   198480 kB
Active(file):    1124984 kB
Inactive(file):   629296 kB
Unevictable:      298124 kB
Mlocked:           13580 kB
SwapTotal:       2097148 kB
SwapFree:        2097148 kB
Dirty:                20 kB
Writeback:             0 kB
AnonPages:       1672132 kB
Mapped:           761996 kB
Shmem:            484688 kB
KReclaimable:     304840 kB
Slab:             366624 kB
SReclaimable:     304840 kB
SUnreclaim:        61784 kB
KernelStack:       14432 kB
PageTables:        46748 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:    18498524 kB
Committed_AS:    6405440 kB
VmallocTotal:   34359738367 kB
VmallocUsed:           0 kB
VmallocChunk:          0 kB
Percpu:             2624 kB
HardwareCorrupted:     0 kB
AnonHugePages:         0 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
CmaTotal:              0 kB
CmaFree:               0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
Hugetlb:               0 kB
DirectMap4k:      191348 kB
DirectMap2M:     8062976 kB
DirectMap1G:    25165824 kB
"""

class TestMiviewer(unittest.TestCase):
    def test_parse_meminfo_line(self):
        mi = parse_meminfo_line({}, "MemAvailable:   29904600 kB")
        self.assertEqual(mi["MemAvailable"], 29904600)
        mi = parse_meminfo_line(mi, "MemAvailable:   12345678 kB")
        self.assertEqual(mi["MemAvailable"], 12345678)

    def test_parse_meminfo(self):
        mi = parse_meminfo(TEST_MEMINFO)
        self.assertEqual(mi["MemAvailable"], 29904600)
        self.assertEqual(mi["SReclaimable"], 304840)
        self.assertEqual(mi["Active(anon)"], 1673760)

if __name__ == "__main__":
    unittest.main()
