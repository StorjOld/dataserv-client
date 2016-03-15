import dataserv_client.bandwidth_test as bt
import unittest
import socket
import time
import threading
import timeit
import os


class TestBandwidthTest(unittest.TestCase):
    def test_bound_socket(self):
        sock_family = socket.AF_INET
        sock_type = socket.SOCK_STREAM
        bt.source = "127.0.0.1"
        sock = bt.bound_socket(sock_family, sock_type)
        self.assertTrue(isinstance(sock, socket.socket))
        
    def test_distance(self):
        coordinate_pairs = {
            1: [[10, 10], [10, 10]],
            2: [[33.7550, 84.3900], [40.7127, 74.0059]],
            3: [[0, 0], [0, 0]],
            4: [[-33.7550, -84.3900], [40.7127, 74.0059]],
        }
        
        results = {
            1: 0.0,
            2: 1200.0,
            3: 0.0,
            4: 17959
        }
        
        for coordinate_pair in coordinate_pairs:
            source, destination = coordinate_pairs[coordinate_pair]
            expected = results[coordinate_pair]
            got = round(bt.distance(source, destination))
            self.assertTrue(expected == got)
            
    def test_build_user_agent(self):
        ua = bt.build_user_agent()
        self.assertTrue(ua != "")
        self.assertTrue(type(ua) in (type(b""), type(u"")))
        
    def test_build_request(self):
        url = "http://storj.io/"
        data = "test"
        headers = {"referer": "http://www.google.com/"}
        r = bt.build_request(url, data, headers)
        self.assertTrue(isinstance(r, bt.Request))
        
        # Invalid URL.
        url = ""
        try:
            r = bt.build_request(url, data, headers)
        except ValueError:
            pass

    def test_catch_request(self):
        # Pass
        r = bt.Request(url="http://www.google.com/")
        r, e = bt.catch_request(r)
        self.assertTrue(r != None)
        
        # Fail without error.
        r = bt.Request(url="http://127.0.0.1:74231/")
        r, e = bt.catch_request(r)
        self.assertTrue(r == None)
        
    def test_file_getter(self):
        bt.shutdown_event = threading.Event()
        file_getter = bt.FileGetter("http://storj.io/", time.time())
        file_getter.run()
        time.sleep(1)
        self.assertTrue(sum(file_getter.result))
        
    def test_download_speed(self):
        bt.shutdown_event = threading.Event()
        files = [
            "http://www.storj.io/",
            "http://www.google.com/"
        ]
        
        self.assertTrue(bt.downloadSpeed(files))
        self.assertFalse(bt.downloadSpeed([]))
        
    def test_file_putter(self):
        bt.shutdown_event = threading.Event()
        file_putter = bt.FilePutter("http://atl.speedtest.pavlovmedia.net/speedtest/upload.php", timeit.default_timer(), 250000)
        file_putter.start()
        file_putter.join()
        self.assertTrue(file_putter.result)
        
    def test_upload_speed(self):
        bt.shutdown_event = threading.Event()
        files = [
            "http://atl.speedtest.pavlovmedia.net/speedtest/upload.php"
        ]
        
        sizes = [250000]
        self.assertTrue(bt.uploadSpeed("http://atl.speedtest.pavlovmedia.net/speedtest/upload.php", sizes, 1))
        self.assertFalse(bt.uploadSpeed("", sizes, 1))
        
    def test_get_config(self):
        # Invalid URL.
        try:
            bt.getConfig(url="test")
        except ValueError:
            pass
            
        # Valid XML.
        configxml = """<?xml version="1.0" encoding="UTF-8"?>
<settings>
<client ip="127.0.0.1" lat="40" lon="-90" isp="Comcast Cable" isprating="2.9" rating="0" ispdlavg="30000" ispulavg="60000" loggedin="0" />
<times dl1="5000000" dl2="35000000" dl3="800000000" ul1="1000000" ul2="8000000" ul3="35000000" />
<download testlength="10" initialtest="250K" mintestsize="250K" threadsperurl="4" />
<upload testlength="10" ratio="5" initialtest="0" mintestsize="32K" threads="2" maxchunksize="512K" maxchunkcount="50" threadsperurl="4" />
</settings>
        """
        self.assertTrue(type(bt.getConfig(configxml=configxml)) is dict)
        
    def test_closest_servers(self):
        configxml = bt.getConfig()
        servers = bt.closestServers(configxml["client"])
        self.assertTrue(len(servers))
        self.assertTrue(type(bt.getBestServer(servers)) is dict)
        
    def test_speed_test_cached(self):
        cache_path = os.path.join(os.getcwd(), "speed_test")
        if os.path.exists(cache_path):
            os.remove(cache_path)
            
        content = """{"download": 1, "upload": 2}"""
        with open(cache_path, "w") as fp:
            fp.write(content)
        
        ret = bt.speed_test_cached()
        self.assertTrue(ret["download"] == 1)
        self.assertTrue(ret["upload"] == 2)

