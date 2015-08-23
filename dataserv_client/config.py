import json
from StringIO import StringIO
from dataserv_client import encryptedio


def load_config(path, password):
    with open(path, 'rb') as in_file, StringIO() as out_file:
        encryptedio.decrypt(in_file, out_file, password)
        return json.loads(out_file.getvalue())


def save_config(path, password, json_serializable):
    with StringIO() as in_file, open(path, 'wb') as out_file:
        in_file.write(json.dumps(json_serializable))
        encryptedio.encrypt(in_file, out_file, password)
