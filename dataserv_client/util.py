import psutil
import os


def get_fs_type(path):  # FIXME find a way to unit test this
    """Returns: path filesystem type or None."""
    partitions = {}
    for partition in psutil.disk_partitions():
        partitions[partition.mountpoint] = (partition.fstype, partition.device)
    if path in partitions:
        return partitions[path][0]
    splitpath = path.split(os.sep)
    for i in range(len(splitpath), 0, -1):
        path = os.sep.join(splitpath[:i]) + os.sep
        if path in partitions:
            return partitions[path][0]
        path = os.sep.join(splitpath[:i])
        if path in partitions:
            return partitions[path][0]
    return None

