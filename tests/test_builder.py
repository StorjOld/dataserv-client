import os
import json
import random
import shutil
import unittest
import tempfile
from datetime import datetime

import partialhash
from dataserv_client.builder import Builder

my_shard_size = 1024 * 128  # 128K 
my_max_size = 1024 * 256  # 256 !
height = int(my_max_size / my_shard_size)
fixtures = json.load(open("tests/fixtures.json"))
addresses = fixtures["addresses"]
url = "http://127.0.0.1:5000"


def _to_bytes(string):
    return string.encode('utf-8')


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.store_path = tempfile.mkdtemp()
        print(self.store_path)

    def tearDown(self):
        shutil.rmtree(self.store_path)

    def test_sha256(self):
        expected = fixtures["test_sha256"]["expected"]
        self.assertEqual(Builder.sha256("storj"), expected)
        self.assertNotEqual(Builder.sha256("not storj"), expected)

    def test_build_seed(self):
        bucket = Builder(addresses["alpha"], my_shard_size, my_max_size)
        hash0 = fixtures["test_build_seed"]["hash0"]
        hash3 = fixtures["test_build_seed"]["hash3"]
        self.assertEqual(bucket.build_seed(0), hash0)
        self.assertEqual(bucket.build_seed(3), hash3)

    def test_builder_build(self):
        # generate shards for testing
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size)
        bucket.build(self.store_path)

        # see if the shards exist
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            print("PATH", path)
            self.assertTrue(os.path.exists(path))

        bucket.clean(self.store_path)

        # generate shards for testing
        bucket = Builder(addresses["gamma"], my_shard_size, my_max_size)
        bucket.build(self.store_path, cleanup=True)

        # see if the shards are deleted
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_clean(self):
        # generate shards for testing
        bucket = Builder(addresses["delta"], my_shard_size, my_max_size)
        bucket.build(self.store_path)

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
        bucket.build(self.store_path)

        # audit
        audit_results = bucket.audit(b"storj", self.store_path, height)
        result0 = fixtures["test_builder_audit"]["result0"]
        result1 = fixtures["test_builder_audit"]["result1"]
        self.assertEqual(audit_results[0], _to_bytes(result0))
        self.assertEqual(audit_results[1], _to_bytes(result1))

        # audit full
        expected = fixtures["test_builder_audit"]["expected"]
        audit_results = bucket.full_audit(b"storj", self.store_path,
                                          height)
        self.assertEqual(audit_results, expected)

    def test_builder_checkup(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        generated = bucket.build(self.store_path)

        # make sure all files are there
        self.assertTrue(bucket.checkup(self.store_path))

        # remove one of the files
        remove_file = random.choice(list(generated.keys()))
        os.remove(os.path.join(self.store_path, remove_file))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.store_path))

    def test_builder_rebuilds(self):
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)

        # generate empty files to be rebuilt
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            with open(path, 'a'):
                os.utime(path, None)

        # rebuild all files
        bucket.build(self.store_path, rebuild=True)

        # audit full
        expected = fixtures["test_builder_audit"]["expected"]
        audit_results = bucket.full_audit(b"storj", self.store_path,
                                          height)
        self.assertEqual(audit_results, expected)

    def test_build_rebuild(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        bucket.build(self.store_path)

        # remove one of the files
        r = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        os.remove(os.path.join(self.store_path, r))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.store_path))

        # rebuild
        bucket.build(self.store_path, rebuild=True)

        # check again, should pass
        self.assertTrue(bucket.checkup(self.store_path))

    def test_build_rebuild_modify(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size)
        bucket.build(self.store_path)

        # modify one of the files
        o = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        path = os.path.join(self.store_path, o)
        sha256_org_file = partialhash.compute(path)

        # write some data
        with open(path, "a") as f:
            f.write("bad data is bad\n")

        # check their hashes
        sha256_mod_file = partialhash.compute(path)
        self.assertNotEqual(sha256_org_file, sha256_mod_file)

        # build without a rebuild should fail
        bucket.build(self.store_path)
        sha256_mod_file = partialhash.compute(path)
        self.assertNotEqual(sha256_org_file, sha256_mod_file)

        # build with a rebuild should pass
        bucket.build(self.store_path, rebuild=True)
        sha256_mod_file = partialhash.compute(path)
        self.assertEqual(sha256_org_file, sha256_mod_file)

    def test_build_cont(self):
        max_size1 = 1024 * 1024 * 384
        max_size2 = 1024 * 1024 * 128

        # generate shards for testing
        start_time = datetime.utcnow()
        bucket = Builder(addresses["epsilon"], my_shard_size, max_size1)
        bucket.build(self.store_path)
        end_delta = datetime.utcnow() - start_time

        # should skip all shards and be faster
        start_time2 = datetime.utcnow()
        bucket = Builder(addresses["epsilon"], my_shard_size, max_size2)
        bucket.build(self.store_path)
        end_delta2 = datetime.utcnow() - start_time2

        self.assertTrue(end_delta2 < end_delta)

    def test_on_generate_shard_callback(self):
        # save callback args
        on_generate_shard_called_with = []

        def on_generate_shard(*args):
            on_generate_shard_called_with.append(args)

        # generate shards for testing
        bucket = Builder(addresses["omega"], my_shard_size, my_max_size,
                         on_generate_shard=on_generate_shard)
        bucket.build(self.store_path)

        # check correct call count
        calls = len(on_generate_shard_called_with)
        self.assertEqual(int(my_max_size / my_shard_size), calls)

        # check height order
        for num in range(calls):
            height = on_generate_shard_called_with[num][0]
            self.assertEqual(num + 1, height)

    def test_use_folder_tree_clean(self):
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size,
                         use_folder_tree=True)
        bucket.build(self.store_path)
        self.assertTrue(bucket.checkup(self.store_path))
        bucket.clean(self.store_path)

        def callback(a, d, files):
            self.assertTrue(len(files) == 0)
        os.walk(self.store_path, callback, None)

    def test_use_folder_tree_cleanup(self):
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size,
                         use_folder_tree=True)
        bucket.build(self.store_path, cleanup=True)

        def callback(a, d, files):
            self.assertTrue(len(files) == 0)
        os.walk(self.store_path, callback, None)

if __name__ == '__main__':
    # import pudb; pu.db # set break point
    unittest.main()
