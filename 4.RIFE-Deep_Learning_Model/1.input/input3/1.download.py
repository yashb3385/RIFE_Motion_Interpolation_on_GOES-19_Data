import subprocess
import os

git_dir = "yashb3385/Data_Samples/main/15fps_moving_car/frames/"
file = os.path.basename(git_dir)
destination = '.'

last_image_no = 326

i = 1
while i < (last_image_no + 1):

    print(f"\nDownloading {i:04d}.png....")
    subprocess.run(f"curl -L -O https://raw.githubusercontent.com/{git_dir}{i:04d}.png", shell=True)
    i += 1

print("\nProcess Completed.\n")
