import os
import shutil

def clean(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    print(f"\nSuccessfully cleaned path : {path}")

clean("input")
clean("output")
print("\n")