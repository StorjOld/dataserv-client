import unittest
from dataserv_client.bandwidth_test import speedtest


class TestBandwidthTest(unittest.TestCase):

    def test_output(self):
        output = speedtest()
        self.assertIsInstance(output, dict)
        self.assertTrue("download" in output)
        self.assertTrue("upload" in output)


if __name__ == '__main__':
    unittest.main()
