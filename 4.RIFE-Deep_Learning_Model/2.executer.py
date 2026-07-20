import sys
from utils.ask import ask_y_n

print("\n\n===============================================================================================================\n\n                             Welcome to Motion Interpolator\n")
print("===============================================================================================================\n")

print("INSTRUCTIONS BEFORE RUNNING :")
print("    1. Please ensure you have installed all the requirements using 1.install_requirements.py.")
print("    2. Please ensure you have 10GB of disk space available for installations.")
print("    3. You can reclaim your consumed space by deleting requirements by executing 4.delete_requirements.py")
print("    4. Please ensure your input data is placed in the designated folders :")
print("        -> 1.input/input1/")
print("        -> 1.input/input2/")
print("        -> 1.input/input3/ ... etc.")
print("    5. .nc files must placed in their respective channel folders (e.g. C01, C02, C13) in input folders.")
print("    6. Allowed file formats: .nc, .png, .mp4 only.\n")

ready = ask_y_n("Have you placed your input files in those folders yet? [y/n] : ")

if ready != 'y':
    print("\nExiting the program. See you soon!\n\n")
    sys.exit()

############################################################################################################################################################################

from utils.nc_imaging import nc_imager
from utils.img_to_vid import png_to_video
from utils.check_format import file_format_check
from utils.move_over import move
from utils.img_to_nc import png_to_nc
from utils import clear
import time
import shutil
import subprocess
import os
import cv2
import re

############################################################################################################################################################################

rife_path = "ECCV2022-RIFE"
nc_img_max_size = 1500 
c_map = "RdYlBu_r"

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
data_input = int(input("\nWhich input do you want to proceed with?\n     -> You have to enter 1 for input1, 2 for input2, 3 for input3 and so on......\n     -> Enter : "))

gpu_flag = ask_y_n("\nDo you strictly want to use your GPU for the processing [y/n] : ")

############################################################################################################################################################################

def execute(path, gpu_flag):
    start_time = time.perf_counter()
    nc_flag = 0
    png_flag = 0
    mp4_flag = 0

    nc_folder_pattern = re.compile(r'^C\d+$', re.IGNORECASE)
    # Regex to match 'C' followed by digits (e.g., C01, C02... C13)

    my_entries = file_format_check(path, nc_folder_pattern)
    if not my_entries:
        return
    if nc_folder_pattern.match(my_entries[0]):
        nc_flag = 1
    elif my_entries[0].lower().endswith(".png"):
        png_flag = 1
    elif my_entries[0].lower().endswith(".mp4"):
        mp4_flag = 1

    # n = int(input("\nFor 2\u207fX Interpolation, Enter the value of n : "))
    n_list = [int(x) for x in input("\nFor 2\u207fX Interpolation, Enter the values of n separated by spaces : ").split()]
    img_output_flag = ask_y_n("\nInterpolated image output will consume significant amount of space :\n     -> Do you want to generate image output [y/n] : ")

    if "input" in path:
        potential_number = path.split("input")[-1]

        if potential_number.isdigit():
            # input_pointer = 1 for input1, 2 for input2, 42 for input42
            input_pointer = int(potential_number)
    
    img_output_path = f"2.output/output{input_pointer}/img_output"
    vid_output_path = f"2.output/output{input_pointer}/video_output"
    nc_output_path = f"2.output/output{input_pointer}/nc_output"
    channel = ""

    scale = 1
    if nc_flag == 1 or png_flag == 1:
        fps = int(input("\nWhat FPS do you want the original video to be (1, 15, 24, 30, 60, ...) ? \n     -> Enter : "))
        if nc_flag == 1:
            print("\n===============================================================================================================\n") # Extracting Images from .nc files....\n\n")
            RGB_flag, channel_ad, data_time_s_to_e = nc_imager(path, f"{rife_path}/input", c_map, nc_img_max_size, None, None)
            if channel_ad == "RGB_":
                channel_no = channel_ad
                channel = channel_ad
            else:
                channel_no = channel_ad[1:3]
                channel = f"C{channel_no}_"
            if img_output_flag == 'y':
                nc_imager(path,f"{img_output_path}/Native_{channel}Images{data_time_s_to_e}" ,c_map, float('inf'), RGB_flag, channel_no)

        elif png_flag == 1:
            data_time_s_to_e = ""

            downscale_flag = ask_y_n("\nFor High Resolution videos, scaling down is recommended\n     -> Do you want to scale down the final video [y/n] : ")

            if downscale_flag == 'y':
                scale = float(input("   Enter scale value [0.25, 0.5, 1.0, 2.0, 4.0] : "))
                if scale in [0.25, 0.5, 1.0, 2.0, 4.0]:
                    pass
                else:
                    print("Scale value must be in [0.25, 0.5, 1.0, 2.0, 4.0].")
                    return

            for filename in my_entries:
                if os.path.isfile(os.path.join(path, filename)):
                    shutil.copy2(f"{path}/{filename}", f"{rife_path}/input")

        print("\n===============================================================================================================\n")
        for n in n_list:
            print(f"Initiating {2**n}X Interpolation...\n\nLoading the Model...\n")
            if gpu_flag == 'y':
                subprocess.run(f"py310 inference_video.py --exp={n} --img=input/ --scale={scale}", shell=True, cwd=rife_path)
            else:
                subprocess.run(f"py inference_video.py --exp={n} --img=input/ --scale={scale}", shell=True, cwd=rife_path)

            print(f"\n->Video Inferencing Completed for {2**n}X Interpolation.\n\n===============================================================================================================\n")

            png_to_video(f"{rife_path}/input", f"{vid_output_path}/original_{channel}{int(fps)}fps{data_time_s_to_e}.mp4", int(fps))
            png_to_video(f"{rife_path}/vid_out", f"{vid_output_path}/final_{channel}{2**n}X_{int((2**n)*fps)}fps{data_time_s_to_e}.mp4", int((2**n)*fps))

            if nc_flag == 1 and channel_no != "RGB_":
                png_to_nc(f"{rife_path}/vid_out", f"{nc_output_path}/{channel}{int(fps)}fps_to_{int((2**n)*fps)}fps_{2**n}X{data_time_s_to_e}", data_time_s_to_e[2:13], data_time_s_to_e[15:27], c_map, channel_no)

            if img_output_flag == 'y':
                print("\n")
                for img in os.listdir(f"{rife_path}/vid_out"):
                    move(f"{rife_path}/vid_out/{img}", f"{img_output_path}/{channel}{int(fps)}fps_to_{int((2**n)*fps)}fps_{2**n}X{data_time_s_to_e}")

    if mp4_flag == 1:
        for video in my_entries:
            if os.path.isfile(os.path.join(path, video)):

                downscale_flag = ask_y_n("\nFor High Resolution videos, scaling down is recommended\n     -> Do you want to scale down the final video [y/n] : ")

                if downscale_flag == 'y':
                    scale = float(input("   Enter scale value [0.25, 0.5, 1.0, 2.0, 4.0] : "))
                    if scale in [0.25, 0.5, 1.0, 2.0, 4.0]:
                        pass
                    else:
                        print("Scale value must be in [0.25, 0.5, 1.0, 2.0, 4.0].")
                        return
                shutil.copy2(f"{path}/{video}", f"{rife_path}")

                vid = cv2.VideoCapture(f"{rife_path}/{video}")
                fps = int(vid.get(cv2.CAP_PROP_FPS))
                vid.release()

                print("\n===============================================================================================================\n")
                for n in n_list:
                    print(f"Initiating {2**n}X Interpolation...\n\nLoading the Model...\n")
                    if gpu_flag == 'y':
                        subprocess.run(f"py310 inference_video.py --exp={n} --video={video} --scale={scale}", shell=True, cwd=rife_path)
                    else:
                        subprocess.run(f"py inference_video.py --exp={n} --video={video} --scale={scale}", shell=True, cwd=rife_path)
                    
                    print(f"\n->Video Inferencing Completed for {2**n}X Interpolation.\n\n===============================================================================================================\n")
                os.remove(f"{rife_path}/{video}")

        for file in os.listdir(f"{rife_path}"):
            if os.path.isfile(os.path.join(f"{rife_path}", file)) and file.lower().endswith('.mp4'):
                if img_output_flag == 'y':
                    target_dir = os.path.join(img_output_path, f"{file[:-4]}")
                    os.makedirs(target_dir, exist_ok=True)
                    ffmpeg_cmd = f'ffmpeg -i "{rife_path}/{file}" -vsync 0 "{target_dir}/%04d.png"'
                    subprocess.run(ffmpeg_cmd, shell=True)

                    print("\n===============================================================================================================\n")

                move(f"{rife_path}/{file}", f"{vid_output_path}")

    reset_rife()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Model execution duration : {int(hours):02d}h {int(minutes):02d}m {seconds:.2f}s\n")

############################################################################################################################################################################

execute(f"1.input/input{data_input}", gpu_flag)