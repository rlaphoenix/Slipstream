# std
import os
import subprocess


def get_mount_path(dev):
    """Use findmnt to get the mounted path of the device"""
    return subprocess.check_output(["findmnt", "-nr", "-o", "target", "-S", dev]).decode().strip()

def mount(dev):
    """Mount device read-only and return mount path"""
    ret = os.system(f"mount -o ro {dev}")
    if ret != 0:
        raise Exception("Mount failed...")
    return get_mount_path(dev)

def unmount(dev):
    """Unmount device or path"""
    ret = os.system(f"umount {dev}")
    if ret != 0:
        raise Exception("Unmount failed...")
