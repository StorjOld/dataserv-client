import os
import bisect
import hashlib
import binascii
from datetime import datetime

import RandomIO
import partialhash


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

    def _build_all_seeds(self,height):
        """Includes seed for height 0."""
        seed = self.sha256(self.address)
        seeds = [seed]
        for i in range(height):
            seed = self.sha256(seed)
            seeds.append(seed)
        return seeds

    def build_seeds(self, height):
        """Deterministically build seeds."""
        return self._build_all_seeds(height)[:height]

    def build_seed(self, height):
        """Deterministically build a seed."""
        return self._build_all_seeds(height).pop()

    def generate_shard(self, seed, store_path, cleanup=False):
        """
        Save a shard, and return its SHA-256 hash.

        :param seed: Seed pased to RandomIO to generate file.
        :param store_path: What path to store the file.
        :param cleanup: Delete the file after generation.
        :return: SHA-256 hash of the file.
        """

        # save the shard
        path = os.path.join(store_path, seed)
        RandomIO.RandomIO(seed).genfile(self.shard_size, path)

        # get the file hash
        with open(path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # remove file if requested
        if cleanup:
            os.remove(path)

        return file_hash

    def filter_to_resume_point(self, store_path, enum_seeds):
        """
        Binary search to find the proper place to resume.

        :param store_path: What path to the files are stored at.
        :param enum_seeds: List of seeds to check.
        :return:
        """

        class HackedCompareObject(str):
            def __gt__(self, seed):
                path = os.path.join(store_path, seed)
                return os.path.exists(path)

        seeds = [seed for num, seed in enum_seeds]
        index = bisect.bisect_left(seeds, HackedCompareObject())

        # rebuild last shard, likely corrupt
        index = index - 1 if index > 0 else index

        if self.debug:
            print("Resuming from height {0}".format(index + 1))
        return enum_seeds[index:]

    def build(self, store_path, cleanup=False, rebuild=False):
        """
        Fill the farmer with data up to their max.

        :param store_path: What path to store the file.
        :param cleanup: Delete the file after generation.
        :param rebuild: Re-generate the shards.
        """

        generated = {}

        enum_seeds = list(enumerate(self.build_seeds(self.target_height)))
        if not rebuild:
            enum_seeds = self.filter_to_resume_point(store_path, enum_seeds)

        for shard_num, seed in enum_seeds:

            file_hash = self.generate_shard(seed, store_path, cleanup=cleanup)
            generated[seed] = file_hash
            if self.debug:
                print("Saving seed {0} with SHA-256 hash {1}.".format(
                    seed, file_hash
                ))

            if self.on_generate_shard:
                self.on_generate_shard(shard_num + 1, seed, file_hash)

        return generated

    def clean(self, store_path):
        """
        Delete shards from path.

        :param store_path: Path the shards are stored at.
        """

        seeds = self.build_seeds(self.target_height)
        for shard_num, seed in enumerate(seeds):
            path = os.path.join(store_path, seed)
            if os.path.exists(path):
                os.remove(path)

    def checkup(self, store_path):
        """
        Make sure the shards exist.

        :param store_path: Path the shards are stored at.
        :return True if all shards exist, False otherwise.
        """

        seeds = self.build_seeds(self.target_height)
        for shard_num, seed in enumerate(seeds):
            path = os.path.join(store_path, seed)
            if not os.path.exists(path):
                return False
        return True

    # Unused Audit Code
    def audit(self, seed, store_path, height):
        """Do an audit over the data."""
        audit_results = []
        seeds = self.build_seeds(height)
        for shard_num, seed_hash in enumerate(seeds):
            seed_path = os.path.join(store_path, seed_hash)
            digest = partialhash.sample(seed_path, 1024, sample_count=3,
                                        seed=seed)
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
