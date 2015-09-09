import hashlib
import unittest
import tempfile
from dataserv_client.control import encryptedio


class TestConfig(unittest.TestCase):

    def test_roundtrip(self):
        input_path = "tests/fixtures.json"
        encrypted_path = tempfile.mktemp()
        output_path = tempfile.mktemp()
        print("encrypted_path", encrypted_path)
        print("output_path", output_path)

        # encrypt
        with open(input_path, 'rb') as in_file, open(encrypted_path, 'wb') as\
                out_file:
            encryptedio.encrypt(in_file, out_file, b"test")

        # decrypt
        with open(encrypted_path, 'rb') as in_file, open(output_path, 'wb') as\
                out_file:
            encryptedio.decrypt(in_file, out_file, b"test")

        # check hashes
        with open(input_path, 'rb') as input_file:
            input_hash = hashlib.sha256(input_file.read()).hexdigest()
        with open(output_path, 'rb') as output_file:
            output_hash = hashlib.sha256(output_file.read()).hexdigest()
        self.assertEqual(input_hash, output_hash)

        # TODO add openssl compatibility tests (already tested manually)


if __name__ == '__main__':
    unittest.main()
