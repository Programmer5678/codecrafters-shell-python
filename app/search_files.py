import os

class File:
    def __init__(self, dir_path, file):
        self._dir_path = dir_path
        self._file = file

    def file(self):
        return self._file

    def dir_path(self):
        return self._dir_path

    def full_path(self):
        return os.path.join(self.dir_path(), self.file())


# -------------------------------
# Utility functions (module-level)
# -------------------------------

def all_dirs(dir_paths):
    """Return only directories from a list of paths."""
    return [d for d in dir_paths if os.path.isdir(d)]


def all_files(dir_paths):
    """Return File objects for all files in the given directories."""
    result = []
    for dir_path in all_dirs(dir_paths):
        for file_name in os.listdir(dir_path):
            f = File(dir_path, file_name)
            if os.path.isfile(f.full_path()):
                result.append(f)
    return result


def all_execs(dir_paths):
    return [ f for f in all_files(dir_paths) if os.access(f.full_path(), os.X_OK) ]

def all_execs_in_path():
    path_dirs = os.environ.get("PATH", "").split(":")
    return all_execs(path_dirs)



def find_in_path(looking_for):
    """Find an executable in the system PATH."""
    for f in all_execs_in_path():
        if f.file() == looking_for:
            return f
        
    return None
