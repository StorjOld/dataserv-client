import os
import unittest
from dataserv_client.builder import Builder

address_alpha = "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm"
address_beta = "1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa"
address_gamma = "1Jd4YBQ7d8nHGe4zWfLL9EWHMkspN9JKGf"
address_delta = "16eEuTp1QERjCC8ZnGf34NvkptMifNSCti"

my_store_path = "tmp/"
my_shard_size = 1024*1024*128  # 128 MB
my_max_size = 1024*1024*256  # 512 MB



class TestBuilder(unittest.TestCase):

    def test_sha256(self):
        ans = 'c059c8035bbd74aa81f4c787c39390b57b974ec9af25a7248c46a3ebfe0f9dc8'
        self.assertEqual(Builder.sha256("storj"), ans)
        self.assertNotEqual(Builder.sha256("not storj"), ans)

    def test_build_seed(self):
        bucket = Builder(address_alpha, 0, 0)  # emtpy bucket

        hash0 = '8f4306631f71e40369acc3fb5645e7d13d17e686a3b623b46b4872714d3e3e92'
        hash3 = '4192fe2dd784eb5bc770258e5a494a3025b43025304def4b088c574dc4fa8821'

        self.assertEqual(bucket.build_seed(0), hash0)
        self.assertEqual(bucket.build_seed(3), hash3)

    def test_builder_build(self):
        # generate shards for testing
        bucket = Builder(address_beta, my_shard_size, my_max_size)
        bucket.build(my_store_path, True, False)

        # see if the shards exist
        for shard_num in range(int(my_max_size / my_shard_size)):
            path = os.path.join(my_store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        # generate shards for testing
        bucket = Builder(address_gamma, my_shard_size, my_max_size)
        bucket.build(my_store_path, True, True)

        # see if the shards are deleted
        for shard_num in range(int(my_max_size / my_shard_size)):
            path = os.path.join(my_store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_clean(self):
        # generate shards for testing
        bucket = Builder(address_delta, my_shard_size, my_max_size)
        bucket.build(my_store_path, False, False)

        # see if the shards exist
        for shard_num in range(int(my_max_size / my_shard_size)):
            path = os.path.join(my_store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        # clean command
        bucket.clean(my_store_path)

        # see if the shards are deleted
        for shard_num in range(int(my_max_size / my_shard_size)):
            path = os.path.join(my_store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))