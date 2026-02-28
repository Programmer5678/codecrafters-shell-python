import os
def absolute(target_path, cwd):

    return os.path.abspath(os.path.join(cwd, os.path.expanduser(target_path)))