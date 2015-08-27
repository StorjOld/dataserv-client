"""
OpenSSL compatible aes file io (source: http://stackoverflow.com/a/16761459)

# usage:
import encryptedio
with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
    encryptedio.encrypt(in_file, out_file, password)
with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
    encryptedio.decrypt(in_file, out_file, password)

# equivalent to:
openssl aes-256-cbc -salt -in filename -out filename.enc
openssl aes-256-cbc -d -in filename.enc -out filename
"""

from hashlib import md5

from Crypto import Random
from Crypto.Cipher import AES


def _chr(i):
    if isinstance(i, bytes):
        return i  # FIXME why is it mixed in python 2 ?
    return chr(i).encode('utf-8')


def _derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = b''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]


def encrypt(in_file, out_file, password, key_length=32):
    assert(isinstance(password, bytes))
    assert(isinstance(key_length, int))
    bs = AES.block_size
    salt = Random.new().read(bs - len(b'Salted__'))
    key, iv = _derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write(b'Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * _chr(padding_length)
            finished = True
        encrypted_chunk = cipher.encrypt(chunk)
        out_file.write(encrypted_chunk)


def decrypt(in_file, out_file, password, key_length=32):
    assert(isinstance(password, bytes))
    assert(isinstance(key_length, int))
    bs = AES.block_size
    salt = in_file.read(bs)[len(b'Salted__'):]
    key, iv = _derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = b''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(_chr(chunk[-1]))
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)
