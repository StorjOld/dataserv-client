import psutil
import os
from dataserv_client import exceptions


def get_fs_type(path):  # FIXME find a way to unit test this
    """Returns: path filesystem type or None."""
    partitions = {}
    for partition in psutil.disk_partitions():
        partitions[partition.mountpoint] = (partition.fstype, partition.device)
    if path in partitions:
        return partitions[path][0]
    splitpath = path.split(os.sep)
    for i in range(len(splitpath), 0, -1):
        subpath = os.sep.join(splitpath[:i]) + os.sep
        if subpath in partitions:
            return partitions[subpath][0]
        subpath = os.sep.join(splitpath[:i])
        if subpath in partitions:
            return partitions[subpath][0]
    raise exceptions.PartitionTypeNotFound(path)


def ensure_path_exists(path):
    """To keep front writing to non-existant paths."""
    if not os.path.exists(path):
        os.makedirs(path)
