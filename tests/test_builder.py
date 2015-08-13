import os
import shutil
import unittest
import tempfile
import partialhash
from datetime import datetime
from dataserv_client.builder import Builder

address_alpha = "12guBkWfVjiqBnu5yRdTseBB7wBM5WSWnm"
address_beta = "1BZR9GHs9a1bBfh6cwnDtvq6GEvNwVWxFa"
address_gamma = "1Jd4YBQ7d8nHGe4zWfLL9EWHMkspN9JKGf"
address_delta = "16eEuTp1QERjCC8ZnGf34NvkptMifNSCti"
address_epsilon = "1FwSLAJtpLrSQp94damzWY2nK5cEBugZfC"

my_shard_size = 1024*1024*128  # 128 MB
my_max_size = 1024*1024*256  # 256 MB
height = int(my_max_size / my_shard_size)


class TestBuilder(unittest.TestCase):

    def setUp(self):
        self.my_store_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.my_store_path)

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
        bucket.build(self.my_store_path, True, False)

        # see if the shards exist
        for shard_num in range(height):
            path = os.path.join(self.my_store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        bucket.clean(self.my_store_path)

        # generate shards for testing
        bucket = Builder(address_gamma, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, True, True)

        # see if the shards are deleted
        for shard_num in range(height):
            path = os.path.join(self.my_store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_clean(self):
        # generate shards for testing
        bucket = Builder(address_delta, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, False, False)

        # see if the shards exist
        for shard_num in range(height):
            path = os.path.join(self.my_store_path, bucket.build_seed(shard_num))
            self.assertTrue(os.path.exists(path))

        # clean command
        bucket.clean(self.my_store_path)

        # see if the shards are deleted
        for shard_num in range(height):
            path = os.path.join(self.my_store_path, bucket.build_seed(shard_num))
            self.assertFalse(os.path.exists(path))

    def test_builder_audit(self):
        # generate shards for testing
        bucket = Builder(address_epsilon, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, False, False)

        # audit
        audit_results = bucket.audit(b"storj", self.my_store_path, height)
        result0 = b'ba5a1733144184f8a9a479048d6e451b3639292f4f805e8eccb27aead92cbf93'
        result1 = b'c790ba29ee4b43218637c84bececc41644e1e03718c824bd41c3adc960da3160'
        self.assertEqual(audit_results[0], result0)
        self.assertEqual(audit_results[1], result1)

        # audit full
        ans = '8d48bf4684c2f8d3bdedfa9b88d29ebdb447263713268bd92a7c7c21881389a2'
        audit_results = bucket.full_audit(b"storj", self.my_store_path, height, True)
        self.assertEqual(audit_results, ans)

    def test_builder_checkup(self):
        # generate shards for testing
        bucket = Builder(address_epsilon, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, False, False)

        # make sure all files are there
        self.assertTrue(bucket.checkup(self.my_store_path))

        # remove one of the files
        remove_file = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        os.remove(os.path.join(self.my_store_path, remove_file))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.my_store_path))

    def test_build_rebuild(self):
        # generate shards for testing
        bucket = Builder(address_epsilon, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, False, False)

        # remove one of the files
        remove_file = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        os.remove(os.path.join(self.my_store_path, remove_file))

        # check again, should fail
        self.assertFalse(bucket.checkup(self.my_store_path))

        # rebuild
        bucket.build(self.my_store_path, False, False)

        # check again, should pass
        self.assertTrue(bucket.checkup(self.my_store_path))

    def test_build_rebuild(self):
        # generate shards for testing
        bucket = Builder(address_epsilon, my_shard_size, my_max_size)
        bucket.build(self.my_store_path, False, False)

        # modify one of the files
        org_file = 'baf428097fa601fac185750483fd532abb0e43f9f049398290fac2c049cc2a60'
        path = os.path.join(self.my_store_path, org_file)
        sha256_org_file = partialhash.compute(path)

        # write some data
        with open(path, "a") as f:
            f.write("bad data is bad\n")
        sha256_mod_file = partialhash.compute(path)

        # check their hashes
        sha256_mod_file = partialhash.compute(path)
        self.assertNotEqual(sha256_org_file, sha256_mod_file)

        # build without a rebuild should fail
        bucket.build(self.my_store_path, False, False, False)
        sha256_mod_file = partialhash.compute(path)
        self.assertNotEqual(sha256_org_file, sha256_mod_file)

        # build with a rebuild should pass
        bucket.build(self.my_store_path, False, False, True)
        sha256_mod_file = partialhash.compute(path)
        self.assertEqual(sha256_org_file, sha256_mod_file)

    def test_build_cont(self):
        max_size1 = 1024*1024*384
        max_size2 = 1024*1024*128

        # generate shards for testing
        start_time = datetime.utcnow()
        bucket = Builder(address_epsilon, my_shard_size, max_size1)
        bucket.build(self.my_store_path, False, False)
        end_delta = datetime.utcnow() - start_time

        # should skip all shards and be faster
        start_time2 = datetime.utcnow()
        bucket = Builder(address_epsilon, my_shard_size, max_size2)
        bucket.build(self.my_store_path, False, False)
        end_delta2 = datetime.utcnow() - start_time2

        self.assertTrue(end_delta2<end_delta)
