import shutil
import os

path = 'C13'
if os.path.exists(path):
    shutil.rmtree(path)
    print(f"\nSuccessfully removed path : {path}\n")