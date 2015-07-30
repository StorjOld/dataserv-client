import os
import hashlib
import RandomIO


# config vars
my_address = "YOUR ADDRESS HERE"
my_store_path = "YOUR ABSOLUTE PATH HERE"
my_shard_size = 1024*1024*128  # 128 MB
my_max_size = 1024*1024*1024  # 1 GB


class Builder:

    def __init__(self, address, shard_size, max_size):
        self.address = address
        self.shard_size = shard_size
        self.max_size = max_size

    @staticmethod
    def sha256(content):
        """Finds the SHA-256 hash of the content."""
        content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    def build_seed(self, height):
        """Deterministically build a seed."""
        seed = self.sha256(self.address)
        for i in range(height):
            seed = self.sha256(seed)
        return seed

    def generate_shard(self, seed, store_path, cleanup=False):
        """Save a shard, and return its SHA-256 hash."""
        tmp_file = RandomIO.RandomIO(seed).read(self.shard_size)  # temporarily generate file
        file_hash = hashlib.sha256(tmp_file).hexdigest()  # get SHA-256 hash
        RandomIO.RandomIO(seed).genfile(self.shard_size, store_path+file_hash)  # save the shard
        if cleanup:
            os.remove(store_path+file_hash)
        return file_hash

    def build(self, store_path, debug=False, cleanup=False):
        """Fill the farmer with data up to their max."""
        for shard_num in range(int(self.max_size/self.shard_size)):
            seed = self.build_seed(shard_num)
            file_hash = self.generate_shard(seed, store_path, cleanup)

            if debug:
                print("Saving seed {0} with SHA-256 hash {1}.".format(seed, file_hash))


if __name__ == "__main__":  # pragma: no cover
    bucket = Builder(my_address, my_shard_size, my_max_size)
    bucket.build(my_store_path, True)
