import os
import hashlib
import RandomIO


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

        # save the shard
        path = os.path.join(store_path, seed)
        RandomIO.RandomIO(seed).genfile(self.shard_size, path)
        file_hash = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        if cleanup:
            os.remove(path)
        return file_hash

    def build(self, store_path, debug=False, cleanup=False):
        """Fill the farmer with data up to their max."""
        hashes = []
        for shard_num in range(int(self.max_size / self.shard_size)):
            seed = self.build_seed(shard_num)
            file_hash = self.generate_shard(seed, store_path, cleanup)
            hashes.append(file_hash)

            if debug:
                print("Saving seed {0} with SHA-256 hash {1}.".format(
                    seed, file_hash
                ))

        return hashes
