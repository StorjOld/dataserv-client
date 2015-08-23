import json


def load(path, password=None):
    if password is None:  # unencrypted
        with open(path, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        raise Exception("encryption not implemented")


def save(path, json_serializable, password=None):
    if password is None:  # unencrypted
        with open(path, 'w') as config_file:
            config_file.write(json.dumps(json_serializable))
    else:
        raise Exception("encryption not implemented")
