import os
import time
import json
import random
import shutil
import unittest
import tempfile
from dataserv_client.builder import Builder


my_shard_size = 1024*1024*128  # 128 MB
my_max_size = 1024*1024*256  # 256 MB
height = int(my_max_size / my_shard_size)
fixtures = json.load(open("tests/fixtures.json"))
addresses = fixtures["addresses"]
url = "http://127.0.0.1:5000"


def _to_bytes(string):
    return string.encode('utf-8')


class TestBuilder(unittest.TestCase):

    def setUp(self):
        self.store_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.store_path)

    def test_sha256(self):
        expected = fixtures["test_sha256"]["expected"]
        self.assertEqual(Builder.sha256("storj"), expected)
        self.assertNotEqual(Builder.sha256("not storj"), expected)

    def test_build_seed(self):
        bucket = Builder(addresses["alpha"], 0, 0)  # emtpy bucket
        hash0 = fixtures["test_build_seed"]["hash0"]
        hash3 = fixtures["test_build_seed"]["hash3"]
        self.assertEqual(bucket.build_seed(0), hash0)
        self.assertEqual(bucket.build_seed(3), hash3)

    def test_builder_build(self):
        # generate shards for testing
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size)
        bucket.build(self.store_path, True, False)

        # see if the shards exist
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        bucket.clean(self.store_path)

        # generate shards for testing
        bucket = Builder(addresses["gamma"], my_shard_size, my_max_size)
        bucket.build(self.store_path, True, True)

        # see if the shards are deleted
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_clean(self):
        # generate shards for testing
        bucket = Builder(addresses["delta"], my_shard_size, my_max_size)
        bucket.build(self.store_path, False, False)

        # see if the shards exist
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        # clean command
        bucket.clean(self.store_path)

        # see if the shards are deleted
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_audit(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        bucket.build(self.store_path, False, False)

        # audit
        audit_results = bucket.audit(b"storj", self.store_path, height)
        result0 = fixtures["test_builder_audit"]["result0"]
        result1 = fixtures["test_builder_audit"]["result1"]
        self.assertEqual(audit_results[0], _to_bytes(result0))
        self.assertEqual(audit_results[1], _to_bytes(result1))

        # audit full
        expected = fixtures["test_builder_audit"]["expected"]
        audit_results = bucket.full_audit(b"storj", self.store_path,
                                          height, True)
        self.assertEqual(audit_results, expected)

    def test_builder_checkup(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        generated = bucket.build(self.store_path, False, False)

        # make sure all files are there
        self.assertTrue(bucket.checkup(self.store_path))

        # remove one of the files
        remove_file = random.choice(list(generated.keys()))
        os.remove(os.path.join(self.store_path, remove_file))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.store_path))

    def test_builder_skips_existing(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        generated = bucket.build(self.store_path, False, False)

        timestamp = time.time()

        # remove one of the files
        remove_file = random.choice(list(generated.keys()))
        os.remove(os.path.join(self.store_path, remove_file))

        # generate only missing shard for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        generated = bucket.build(self.store_path, False, False)

        # verify last access times
        for seed, file_hash in generated.items():
            path = os.path.join(self.store_path, seed)
            last_access = os.path.getmtime(path)
            if seed == remove_file:
                self.assertTrue(last_access > timestamp)
            else:
                self.assertTrue(last_access < timestamp)

        # make sure all files are there
        self.assertTrue(bucket.checkup(self.store_path))

    def test_builder_rebuilds(self):
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)

        # generate empty files to be rebuilt
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            with open(path, 'a'):
                os.utime(path, None)

        # rebuild all files
        bucket.build(self.store_path, debug=False, cleanup=False, rebuild=True)

        # audit full
        expected = fixtures["test_builder_audit"]["expected"]
        audit_results = bucket.full_audit(b"storj", self.store_path,
                                          height, True)
        self.assertEqual(audit_results, expected)
