import sys
from utils.ask import ask_y_n

ready = ask_y_n("\nPlease ensure you have 10GB of disk space available for installations.\n      -> Are you Ready [y/n] : ")

if ready != 'y':
    print("\nExiting the program. See you soon!\n\n")
    sys.exit()
print("\n\n")

############################################################################################################################################################################

import os
import shutil
import subprocess

############################################################################################################################################################################

rife_path = "ECCV2022-RIFE"

user_profile = os.environ["USERPROFILE"]

python310 = os.path.join(user_profile, "AppData", "Local", "Programs", "Python", "Python310")

src_python = os.path.join(python310, "python.exe")
dst_py310 = os.path.join(python310, "py310.exe")

src_pip = os.path.join(python310, "Scripts", "pip.exe")
src_pip3 = os.path.join(python310, "Scripts", "pip3.exe")
dst_pip310 = os.path.join(python310, "Scripts", "pip310.exe")

############################################################################################################################################################################

print("Searching/Installing Python 3.10...")
subprocess.run(["winget", "install", "Python.Python.3.10"], shell=True, cwd=user_profile)

print("\nProceeding to clean py310......")
try:
    os.remove(dst_py310)
    print("   ->Successfully cleaned py310.\n")
except:
    print("   ->py310 doesn't exist.\n")

print("Proceeding to clean pip310......")
try:
    os.remove(dst_pip310)
    print("   ->Successfully cleaned pip310.\n")
except:
    print("   ->pip310 doesn't exist.\n")

try:
    if os.path.exists(src_python):
        shutil.copy2(src_python, dst_py310)
        print("\nSuccessfully renamed python.exe to py310.exe")
        print("Made python.exe exclusively executable for global version.")

    if os.path.exists(src_pip):
        os.rename(src_pip, dst_pip310)
    elif os.path.exists(src_pip3):
        shutil.copy2(src_pip3, dst_pip310)
    print("\nSuccessfully renamed pip.exe to pip310.exe")
    print("Made pip.exe exclusively executable for global version.")

except FileNotFoundError:
    print("\n[Warning]: Could not modify files. Python 3.10 directory structure wasn't found.")
    print("Ensure the installation path is exactly correct.")

print("\n---------------------------------------------------------------------\npython --version :")
subprocess.run("python --version", shell=True)
print("\npy310 --version :")
subprocess.run("py310 --version", shell=True)
print("\npy --version :")
subprocess.run("py --version", shell=True)
print("---------------------------------------------------------------------")
subprocess.run("pip310", shell=True)
print("\n---------------------------------------------------------------------\n")

############################################################################################################################################################################
############################################################################################################################################################################

subprocess.run("winget install curl.curl", shell=True, cwd=user_profile)
subprocess.run("winget install Gyan.FFmpeg", shell=True, cwd=user_profile)

subprocess.run("pip install netCDF4 matplotlib requests xarray opencv-python scipy", shell=True, cwd=user_profile)
# subprocess.run("pip install phasepack", shell=True, cwd=user_profile)
# subprocess.run("pip install image-similarity-measures --no-deps", shell=True, cwd=user_profile)

subprocess.run("pip310 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121", shell=True, cwd=rife_path)
subprocess.run("pip310 install -r requirements.txt", shell=True, cwd=rife_path)