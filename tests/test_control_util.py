import unittest
from dataserv_client.control import util


class TestControlUtil(unittest.TestCase):

    def test_chunks(self):
        self.assertEqual(
            util.chunks([1,2,3,4,5,6,7,8], 3),
            [[1, 2, 3], [4, 5, 6], [7, 8]]
        )

    def test_baskets(self):
        self.assertEqual(
            util.baskets([1,2,3,4,5,6,7,8, 9, 10], 3),
            [[1, 4, 7, 10], [2, 5, 8], [3, 6, 9]]
        )

# TODO test get_fs_type

if __name__ == '__main__':
    unittest.main()
