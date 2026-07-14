import subprocess
import os
import shutil
import sys

def ask_y_n(ques):
    while True:
        ans = input(ques).strip().lower()
        if ans in ['y', 'n']:
            break 
        print("Invalid input! Please enter exactly 'y' or 'n'.\n")
    return ans

ready = ask_y_n("\nAre you sure to delete all requirements [y/n] : ")

if ready != 'y':
    print("\nExiting the program. See you soon!\n\n")
    sys.exit()

print("\n\n")

rife_path = "ECCV2022-RIFE"
user_profile = os.environ["USERPROFILE"]

python310 = os.path.join(user_profile, "AppData", "Local", "Programs", "Python", "Python310")

python = os.path.join(python310, "python.exe")
py310 = os.path.join(python310, "py310.exe")

pip = os.path.join(python310, "Scripts", "pip.exe")
pip3 = os.path.join(python310, "Scripts", "pip3.exe")
pip310 = os.path.join(python310, "Scripts", "pip310.exe")
###########################################################################################

print("Searching/Installing Python 3.10...")
subprocess.run(["winget", "install", "Python.Python.3.10"], shell=True, cwd=user_profile)

print("\nProceeding to clean pip310......")
try:
    os.remove(pip310)
    print("   ->Successfully cleaned pip310.\n")
except:
    print("   ->pip310 doesn't exist.\n")

try:
    if os.path.exists(pip):
        os.rename(pip, pip310)
    elif os.path.exists(pip3):
        shutil.copy2(pip3, pip310)
    print("\nSuccessfully renamed pip.exe to pip310.exe")
    print("Made pip.exe exclusively executable for global version.")

except FileNotFoundError:
    print("\n[Warning]: Could not modify files. Python 3.10 directory structure wasn't found.")
    print("Ensure the installation path is exactly correct.")
###########################################################################################

subprocess.run("pip310 freeze > remove_all_packages.txt", shell=True, cwd=user_profile)
subprocess.run("pip310 uninstall -r remove_all_packages.txt -y", shell=True, cwd=user_profile)

requirements = os.path.join(user_profile, "remove_all_packages.txt")
if os.path.exists(requirements):
    os.remove(requirements)

################################################################################################
print("\nProceeding to clean py310......")
try:
    os.remove(py310)
    print("   ->Successfully cleaned py310.\n")
except:
    print("   ->py310 doesn't exist.\n")

print("Proceeding to clean pip310......")
try:
    os.remove(pip310)
    print("   ->Successfully cleaned pip310.\n")
except:
    print("   ->pip310 doesn't exist.\n")

print("\n")
subprocess.run(["winget", "uninstall", "Python.Python.3.10"], shell=True, cwd=user_profile)
print("\n")