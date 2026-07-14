import subprocess
import zipfile
import os

git_file_path = "yashb3385/Data_Samples/main/15fps_moving_car/video/15fps.mp4"
file = os.path.basename(git_file_path)
destination = '.'

print("\n")
subprocess.run(f"curl -L -O https://raw.githubusercontent.com/{git_file_path}", shell=True)
print("\n")