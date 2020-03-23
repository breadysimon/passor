import os


def get_src_path(file, *args):
    """get full path of the source file and join the path."""
    return os.path.join(os.path.dirname(os.path.realpath(file)), *args)
