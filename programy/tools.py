__all__ = ["tools"]

import sys
import subprocess
import os


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
