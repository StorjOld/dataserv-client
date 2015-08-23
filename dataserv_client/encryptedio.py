"""
OpenSSL compatible aes file io (source: http://stackoverflow.com/a/16761459)

# usage:
with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
    encrypt(in_file, out_file, password)
with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
    decrypt(in_file, out_file, password)

# equivalent to:
openssl aes-256-cbc -salt -in filename -out filename.enc
openssl aes-256-cbc -d -in filename.enc -out filename
"""

# FIXME add unittests to ensure compatibility (already verified manually)


from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random


def _derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]


def encrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = _derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))


def decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = _derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)


