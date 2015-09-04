import psutil


# source http://stackoverflow.com/a/25286268
def get_fs_type(path):
    root_type = ""
    for partition in psutil.disk_partitions():
        if partition.mountpoint == '/':
            root_type = partition.fstype
            continue
        if path.startswith(partition.mountpoint):
            return partition.fstype
    return root_type
