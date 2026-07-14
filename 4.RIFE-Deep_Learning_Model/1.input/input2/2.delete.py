import os

path = '15fps.mp4'
if os.path.exists(path):
    os.remove(path)
    print(f"\nSuccessfully removed path : {path}\n")