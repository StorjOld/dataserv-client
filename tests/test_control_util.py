import os
import unittest
from dataserv_client.control import util
from dataserv_client import exceptions


class TestControlUtil(unittest.TestCase):

    def test_chunks(self):
        self.assertEqual(
            util.chunks([1, 2, 3, 4, 5, 6, 7, 8], 3),
            [[1, 2, 3], [4, 5, 6], [7, 8]]
        )

    def test_baskets(self):
        self.assertEqual(
            util.baskets([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3),
            [[1, 4, 7, 10], [2, 5, 8], [3, 6, 9]]
        )

    def test_get_fs_type(self):
        fstypes = ["xfs", "ext4", "ext", "vfat", "ntfs"]

        # test positile
        fstype = util.get_fs_type(os.path.realpath(__file__))
        self.assertTrue(fstype in fstypes)

        # test negative
        fstype = util.get_fs_type("bad/path")
        self.assertEqual(fstype, None)


if __name__ == '__main__':
    unittest.main()
