import os
def absolute(target_path, cwd):

    def is_absolute(path):
        return path[0] == '/'

    def is_home_dir(path):
        return path == "~"

    def home_dir():
        return os.path.expanduser("~")

    if is_absolute(target_path):
        return os.path.abspath(target_path)

    elif is_home_dir(target_path):
        return home_dir()

    else:
        return os.path.abspath(os.path.join(cwd , target_path))