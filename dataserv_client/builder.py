import os
import hashlib
import RandomIO
import binascii
import partialhash
import bisect
from datetime import datetime


class Builder:

    def __init__(self, address, shard_size, max_size, on_generate_shard=None,
                 debug=False):
        self.debug = debug
        self.target_height = int(max_size / shard_size)
        self.address = address
        self.shard_size = shard_size
        self.max_size = max_size
        self.on_generate_shard = on_generate_shard

    @staticmethod
    def sha256(content):
        """Finds the SHA-256 hash of the content."""
        content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()

# FIXME how is this not equivelant to the methods below
#   def build_seeds(self, height):
#       """Deterministically build seeds."""
#       seed = self.sha256(self.address)
#       seeds = []
#       for i in range(height):
#           seed = self.sha256(seed)
#           seeds.append(seed)
#       return seeds if seeds else [seed]

#   def build_seed(self, height):
#       """Deterministically build a seed."""
#       return self.build_seeds(height).pop()

    def build_seed(self, height):
        """Deterministically build a seed."""
        seed = self.sha256(self.address)
        for i in range(height):
            seed = self.sha256(seed)
        return seed

    def build_seeds(self, height):
        return list(map(self.build_seed, range(height)))

    def generate_shard(self, seed, store_path, cleanup=False, rebuild=False):
        """Save a shard, and return its SHA-256 hash."""

        # save the shard
        path = os.path.join(store_path, seed)
        if not os.path.isfile(path) or rebuild:
            RandomIO.RandomIO(seed).genfile(self.shard_size, path)

        with open(path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            if cleanup:
                os.remove(path)
            return file_hash

    def filter_to_resume_point(self, store_path, enum_seeds):
        class HackedCompareObject(str):
            def __lt__(self, seed):
                path = os.path.join(store_path, seed)
                return not os.path.exists(path)
        seeds = [seed for num, seed in enum_seeds]
        index = bisect.bisect_left(seeds, HackedCompareObject())
        if self.debug:
            print("Resuming from height {0}".format(index +1))
        return enum_seeds[index:]  # rebuild last in case its corrupt

    def build(self, store_path, cleanup=False, rebuild=False):
        """Fill the farmer with data up to their max.
        Returns: { seed : hash, ... }
        """
        generated = {}

        enum_seeds = list(enumerate(self.build_seeds(self.target_height)))
        if not rebuild:
            enum_seeds = self.filter_to_resume_point(store_path, enum_seeds)

        for shard_num, seed in enum_seeds:

            file_hash = self.generate_shard(seed, store_path, cleanup=cleanup,
                                            rebuild=rebuild)
            generated[seed] = file_hash
            if self.debug:
                print("Saving seed {0} with SHA-256 hash {1}.".format(seed, file_hash))

            if self.on_generate_shard:
                self.on_generate_shard(shard_num + 1, seed, file_hash)

        return generated

    def clean(self, store_path):
        """Delete shards from path."""
        seeds = self.build_seeds(self.target_height)
        for shard_num, seed in enumerate(seeds):
            path = os.path.join(store_path, seed)
            if os.path.exists(path):
                os.remove(path)

    def audit(self, seed, store_path, height):
        """Do an audit over the data."""
        audit_results = []
        seeds = self.build_seeds(height)
        for shard_num, seed in enumerate(seeds):
            seed_path = os.path.join(store_path, seed)
            digest = partialhash.sample(seed_path, 1024, sample_count=3,
                                        seed=seed.encode("utf-8"))
            audit_results.append(binascii.hexlify(digest))
        return audit_results

    def full_audit(self, seed, store_path, height):
        """Compute one hash from audit."""
        hash_result = ""

        start_time = datetime.utcnow()
        audit_results = self.audit(seed, store_path, height)
        for audit in audit_results:
            hash_result += str(audit.decode("utf-8"))
        hash_result = self.sha256(hash_result)

        if self.debug:
            final_time = (datetime.utcnow() - start_time).seconds
            msg = "Seed: {0} with Audit Result: {1} in {2} seconds."
            print(msg.format(str(seed), hash_result, final_time))

        return hash_result

    def checkup(self, store_path):
        """Make sure the shards exist."""
        seeds = self.build_seeds(self.target_height)
        for shard_num, seed in enumerate(seeds):
            path = os.path.join(store_path, seed)
            if not os.path.exists(path):
                return False
        return True


