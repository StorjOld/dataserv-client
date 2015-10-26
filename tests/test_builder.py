import os
import json
import random
import shutil
import unittest
import tempfile
import json
from random import randint
from datetime import datetime

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import partialhash
from dataserv_client.builder import Builder
from dataserv_client import common

my_shard_size = 1024 * 128  # 128K 
my_max_size = 1024 * 256  # 256K
my_min_free_size = 1024 * 256 # 256K
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
        bucket = Builder(addresses["alpha"], my_shard_size, my_max_size,
                         my_min_free_size)
        hash0 = fixtures["test_build_seed"]["hash0"]
        hash3 = fixtures["test_build_seed"]["hash3"]
        self.assertEqual(bucket.build_seed(0), hash0)
        self.assertEqual(bucket.build_seed(3), hash3)

    def test_builder_build(self):
        # generate shards for testing
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size,
                         my_min_free_size)
        bucket.build(self.store_path)

        # see if the shards exist
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            print("PATH", path)
            self.assertTrue(os.path.exists(path))

        bucket.clean(self.store_path)

        # generate shards for testing
        bucket = Builder(addresses["gamma"], my_shard_size, my_max_size,
                         my_min_free_size)
        bucket.build(self.store_path, cleanup=True)

        # see if the shards are deleted
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            self.assertFalse(os.path.exists(path))

    def test_builder_clean(self):
        # generate shards for testing
        bucket = Builder(addresses["delta"], my_shard_size, my_max_size,
                         my_min_free_size)
        bucket.build(self.store_path)

        # see if the shards exist
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            self.assertTrue(os.path.exists(path))

        # clean command
        bucket.clean(self.store_path)

        # see if the shards are deleted
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            self.assertFalse(os.path.exists(path))

    def test_builder_audit(self):
        bucket = Builder(addresses["epsilon"], my_shard_size, 0,
                         my_min_free_size)

        # check last confirmed bitcoin hash
        btc_block = bucket.btc_last_confirmed_block()

        self.assertTrue(btc_block['confirmations']>=
                        common.DEFAULT_MIN_CONFIRMATIONS)
        self.assertTrue(btc_block['is_orphan']==False)

        index = btc_block['block_no']

        block_pos = index % common.DEFAULT_FULL_AUDIT
        block_size = common.DEFAULT_BLOCK_SIZE
        
        # create empty files to skip to btc_index
        seeds = bucket.build_seeds(block_pos * block_size)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            open(path,'w').close()

        # generate shards for audit
        shard_size = my_shard_size * (block_pos + 1) * block_size
        bucket = Builder(addresses["epsilon"], my_shard_size, shard_size,
                         my_min_free_size)
        bucket.build(self.store_path)

        # audit possible
        good_hash = bucket.audit(self.store_path, 
                                 btc_block['block_no'], 
                                 btc_block['blockhash'])
        self.assertTrue(good_hash)

        seeds = bucket.build_seeds((block_pos + 1) * block_size)

        # copy a bad file for a bad audit
        path1 = os.path.join(self.store_path, seeds[-2])
        path2 = os.path.join(self.store_path, seeds[-1])
        shutil.copyfile(path1, path2)
        bad_hash = bucket.audit(self.store_path,
                                btc_block['block_no'],
                                btc_block['blockhash'])

        self.assertFalse(good_hash==bad_hash)

        # write some bad data
        with open(path2, "a") as f:
            f.write("bad data is bad\n")

        # audit failed because last shard has bad data
        self.assertFalse(bucket.audit(self.store_path,
                                      btc_block['block_no'],
                                      btc_block['blockhash']))

        # remove last shard
        os.remove(path2)

        # audit failed because last shard missing
        self.assertFalse(bucket.audit(self.store_path,
                                      btc_block['block_no'],
                                      btc_block['blockhash']))

        # build last shard again
        bucket = Builder(addresses["epsilon"], my_shard_size, shard_size,
                         my_min_free_size)
        bucket.build(self.store_path)

        # audit possible
        good_hash = bucket.audit(self.store_path,
                                 btc_block['block_no'],
                                 btc_block['blockhash'])
        self.assertTrue(good_hash)

        # remove first shard of that block
        path1 = os.path.join(self.store_path, seeds[-80])
        os.remove(path1)

        # audit failed because first shard missing
        self.assertFalse(bucket.audit(self.store_path,
                                      btc_block['block_no'],
                                      btc_block['blockhash']))

    def test_builder_checkup(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size,
                         my_min_free_size)
        generated = bucket.build(self.store_path)

        # make sure all files are there
        self.assertTrue(bucket.checkup(self.store_path))

        # remove one of the files
        remove_file = random.choice(list(generated.keys()))
        os.remove(os.path.join(self.store_path, remove_file))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.store_path))

    def test_builder_rebuilds(self):
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size,
                         my_min_free_size)

        # generate empty files to be rebuilt
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            with open(path, 'a'):
                os.utime(path, None)

        # rebuild all files
        bucket.build(self.store_path, rebuild=True)

    def test_build_rebuild(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size,
                         my_min_free_size)
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
    
    def test_build_repair(self):
        # generate shards for testing
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size,
                         my_min_free_size)
        bucket.build(self.store_path)

        # remove one of the files
        r = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        os.remove(os.path.join(self.store_path, r))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.store_path))

        # repair
        bucket.build(self.store_path, repair=True)

        # check again, should pass
        self.assertTrue(bucket.checkup(self.store_path))

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

        # build without a repair should fail
        bucket.build(self.store_path)
        sha256_mod_file = partialhash.compute(path)
        self.assertNotEqual(sha256_org_file, sha256_mod_file)

        # build with a repair should pass
        bucket.build(self.store_path, repair=True)
        sha256_mod_file = partialhash.compute(path)
        self.assertEqual(sha256_org_file, sha256_mod_file)

    def test_build_cont(self):
        max_size1 = 1024 * 1024 * 384
        max_size2 = 1024 * 1024 * 128

        # generate shards for testing
        start_time = datetime.utcnow()
        bucket = Builder(addresses["epsilon"], my_shard_size, max_size1,
                         my_min_free_size)
        bucket.build(self.store_path)
        end_delta = datetime.utcnow() - start_time

        # should skip all shards and be faster
        start_time2 = datetime.utcnow()
        bucket = Builder(addresses["epsilon"], my_shard_size, max_size2,
                         my_min_free_size)
        bucket.build(self.store_path)
        end_delta2 = datetime.utcnow() - start_time2

        self.assertTrue(end_delta2 < end_delta)

        # delete 10% random files
        my_height = int(max_size2 / my_shard_size)
        seeds = bucket.build_seeds(height)
        for seed in seeds:
            path = os.path.join(self.store_path, seed)
            if randint(0,9)==0:
                os.remove(path)

        # should rebuild missing shards and be slower as skip all 
        # but faster as new build
        start_time3 = datetime.utcnow()
        bucket = Builder(addresses["epsilon"], my_shard_size, max_size2,
                         my_min_free_size)
        bucket.build(self.store_path, repair=True)
        end_delta3 = datetime.utcnow() - start_time3

        self.assertTrue(end_delta3 < end_delta) # faster than new build
        self.assertTrue(end_delta3 > end_delta2) # slower than skip all

    def test_on_generate_shard_callback(self):
        # save callback args
        on_generate_shard_called_with = []

        def on_generate_shard(*args):
            on_generate_shard_called_with.append(args)

        # generate shards for testing
        bucket = Builder(addresses["omega"], my_shard_size, my_max_size,
                         my_min_free_size,
                         on_generate_shard=on_generate_shard)
        bucket.build(self.store_path)

        # check correct call count (+1 call for last height)
        calls = len(on_generate_shard_called_with)
        self.assertEqual(int(my_max_size / my_shard_size) + 1, calls)

        # check height order
        for num in range(calls - 1):
            height = on_generate_shard_called_with[num][0]
            self.assertEqual(num + 1, height)

    def test_use_folder_tree_clean(self):
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size,
                         my_min_free_size,
                         use_folder_tree=True)
        bucket.build(self.store_path)
        self.assertTrue(bucket.checkup(self.store_path))
        bucket.clean(self.store_path)

        def callback(a, d, files):
            self.assertTrue(len(files) == 0)
        os.walk(self.store_path, callback, None)

    def test_use_folder_tree_cleanup(self):
        bucket = Builder(addresses["beta"], my_shard_size, my_max_size,
                         my_min_free_size,
                         use_folder_tree=True)
        bucket.build(self.store_path, cleanup=True)

        def callback(a, d, files):
            self.assertTrue(len(files) == 0)
        os.walk(self.store_path, callback, None)

    def test_on_KeyboardInterrupt(self):
        def _raise(height, last):
            if not last: # only raise 1 of 2 calls
                raise KeyboardInterrupt()

        # generate 1 file with KeyboadInterrupt
        bucket = Builder(addresses["epsilon"], my_shard_size, my_max_size,
                         my_min_free_size, on_generate_shard=_raise)
        self.assertTrue(bucket.build(store_path=self.store_path))
        
        # 1 of 2 files exists and no bad files
        for shard_num in range(height):
            path = os.path.join(self.store_path, bucket.build_seed(shard_num))
            if shard_num <= 0:
                self.assertTrue(os.path.exists(path) 
                                and os.path.getsize(path) == my_shard_size)
            else:
                self.assertFalse(os.path.exists(path))

if __name__ == '__main__':
    # import pudb; pu.db # set break point
    unittest.main()
