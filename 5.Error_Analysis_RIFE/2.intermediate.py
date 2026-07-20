import sys
from utils.ask import ask_y_n

print("\n\n===============================================================================================================\n\n                             Welcome to Motion Interpolator\n")
print("===============================================================================================================\n")

print("INSTRUCTIONS BEFORE RUNNING :")
print("    1. Please ensure you have installed all the requirements using 1.install_requirements.py.")
print("    2. Please ensure you have 10GB of disk space available for installations.")
print("    3. Please ensure your input data is placed in the input folder.")
print("    4. .nc files must placed in their respective channel folders (e.g. C01, C02, C13) in the input folder.")
print("    5. Allowed file format is .nc only.\n")

ready = ask_y_n("Have you placed your input files in input folder yet? [y/n] : ")

if ready != 'y':
    print("\nExiting the program. See you soon!\n\n")
    sys.exit()

############################################################################################################################################################################

from utils.nc_imaging import nc_imager
from utils.check_format import file_format_check
from utils.img_to_nc import png_to_inter_nc
from pathlib import Path
from utils import clear
import time
import subprocess
import os
import re

############################################################################################################################################################################

parent_dir = Path.cwd().parent

rife_path = os.path.join(parent_dir,"4.RIFE-Deep_Learning_Model" ,"ECCV2022-RIFE")

input_path = "input"
output_path = "intermediate"

intermediate_png_path = os.path.join(rife_path, "vid_out", "0000001.png")
nc_img_max_size = 1500 
c_map = "gray"
interpolation_vlaue = 1 # vlaue of n for 2^n X interpolation

# Note on 'cmap': 
# 'gray' provides normal grayscale.
# 'gray_r' provides inverted grayscale (standard for thermal satellite imagery).
# 'turbo', 'jet', 'RdYlBu_r', etc. also can be used for colored mapping.

############################################################################################################################################################################

def reset_rife():
    print("\n===============================================================================================================\n\nResetting the Model-RIFE :")
    clear.clear_folder(f"{rife_path}/input")
    clear.clear_folder(f"{rife_path}/vid_out")
    clear.clear_extenction(f"{rife_path}", '.mp4')  
    print("\n===============================================================================================================\n")

reset_rife()

print("                             Great! Proceeding with motion interpolation...\n")

gpu_flag = ask_y_n("\nDo you strictly want to strictly use your GPU for the processing [y/n] : ")

############################################################################################################################################################################

def execute(path, gpu_flag):
    start_time = time.perf_counter()

    nc_folder_pattern = re.compile(r'^C\d+$', re.IGNORECASE)
    # Regex to match 'C' followed by digits (e.g., C01, C02... C13)

    my_entries = file_format_check(path, nc_folder_pattern)
    if not my_entries:
        return

    channel = ""

    print("\n===============================================================================================================\n") # Extracting Images from .nc files....\n\n")
    channel_ad= nc_imager(path, f"{rife_path}/input", c_map, nc_img_max_size, None)

    channel_no = channel_ad[1:3]
    channel = f"C{channel_no}"

    print("\n===============================================================================================================\n")

    print(f"Initiating {2**interpolation_vlaue}X Interpolation...\n\nLoading the Model...\n")
    if gpu_flag == 'y':
        subprocess.run(f"py310 inference_video.py --exp={interpolation_vlaue} --img=input/", shell=True, cwd=rife_path)
    else:
        subprocess.run(f"py inference_video.py --exp={interpolation_vlaue} --img=input/", shell=True, cwd=rife_path)

    print(f"\n->Video Inferencing Completed for {2**interpolation_vlaue}X Interpolation.\n\n===============================================================================================================\n")

    inter_folder = Path(os.path.join(output_path, channel))
    filenames_tuple = tuple(p.name for p in inter_folder.glob("*.nc") if "inter" not in p.name)

    if filenames_tuple:
        inter_name = filenames_tuple[0] 
    else:
        print("\nNo .nc original intermediate file found.\n")
        return

    png_to_inter_nc(intermediate_png_path, f"{output_path}/{channel}", inter_name, c_map, channel_no)

    reset_rife()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Model execution duration : {int(hours):02d}h {int(minutes):02d}m {seconds:.2f}s\n")

############################################################################################################################################################################

execute(input_path, gpu_flag)