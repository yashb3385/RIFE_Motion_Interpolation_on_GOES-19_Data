import time

import sys

def ask_y_n(ques):
    while True:
        ans = input(ques).strip().lower()
        if ans in ['y', 'n']:
            break 
        print("\nInvalid input! Please enter exactly 'y' or 'n'.\n")
    return ans

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
print("    5. Allowed file formats: .nc, .png, .mp4 only.\n")

ready = ask_y_n("Have you placed your input files in those folders yet? [y/n] : ")

if ready != 'y':
    print("\nExiting the program. See you soon!\n\n")
    sys.exit()

############################################################################################################################################################################

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import shutil
import subprocess
import os
import cv2
import re
import glob
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

############################################################################################################################################################################

rife_path = "ECCV2022-RIFE"
nc_img_max_size = 1500 
c_map = "RdYlBu_r"
blue_cmap = LinearSegmentedColormap.from_list("black_blue", ["black", "blue"])
green_cmap = LinearSegmentedColormap.from_list("black_green", ["black", "green"])
red_cmap = LinearSegmentedColormap.from_list("black_red", ["black", "red"])

# Note on 'cmap': 
# 'gray' provides normal grayscale.
# 'gray_r' provides inverted grayscale (standard for thermal satellite imagery).
# 'turbo', 'jet', 'RdYlBu_r', etc. also can be used for colored mapping.

############################################################################################################################################################################

def clear_folder(folder_path): 
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        
    os.makedirs(folder_path) 
    print(f"     -> {folder_path} successfully emptied!")

############################################################################################################################################################################

def clear_extenction(folder_path, extenction):
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if os.path.isfile(full_path) and filename.lower().endswith(extenction):
            try:
                os.remove(full_path)
                print(f"     -> Deleted: {filename}")
            except PermissionError:
                print(f"\n     -> Could not delete {filename} because it is currently in use by another program.")
            except Exception as e:
                print(f"\n     -> Failed to delete {filename}: {e}")

############################################################################################################################################################################

def reset_rife():
    print("\n===============================================================================================================\n\nResetting the Model-RIFE :")
    clear_folder(f"{rife_path}/input")
    clear_folder(f"{rife_path}/vid_out")
    clear_extenction(f"{rife_path}", '.mp4')  
    print("\n===============================================================================================================\n")

reset_rife()

print("                             Great! Proceeding with motion interpolation...\n")
data_input = int(input("\nWhich input do you want to proceed with?\n     -> You have to enter 1 for input1, 2 for input2, 3 for input3 and so on......\n     -> Enter : "))

gpu_flag = ask_y_n("\nDo you want to use your GPU for the processing [y/n] : ")

############################################################################################################################################################################

def move(source_path, destination_folder):
    filename = os.path.basename(source_path)
    target_file_path = os.path.join(destination_folder, filename)

    if destination_folder:
        os.makedirs(destination_folder, exist_ok=True)

    if os.path.isfile(target_file_path):
        os.remove(target_file_path)
        print(f"->Existing file '{filename}' was overwritten.")
        
    shutil.move(source_path, destination_folder)

############################################################################################################################################################################

def rgb_img_creater(channels_paths, output_path, img_max_pixel):
    file_c01 = channels_paths['C01']
    file_c02 = channels_paths['C02']
    file_c03 = channels_paths['C03']

    def load_and_clean(file_path):
        print(f"    Reading: {os.path.basename(file_path)}")
        with xr.open_dataset(file_path, engine="netcdf4") as ds:
            data = ds['Rad'].values
        return np.nan_to_num(data, nan=0.0)

    R = load_and_clean(file_c02)
    B = load_and_clean(file_c01)
    G_veg = load_and_clean(file_c03)

    if R.shape != B.shape:
        print(f"    Shape mismatch! Adjusting Red channel resolution {R.shape} to match Blue {B.shape}...")
        R = R[::2, ::2]

    def normalize_channel(band_array):
        vmin = np.percentile(band_array, 1)
        vmax = np.percentile(band_array, 99)
        clipped = np.clip(band_array, vmin, vmax)
        if vmax == vmin:
            return np.zeros_like(clipped)
        return (clipped - vmin) / (vmax - vmin)

    print("    Normalizing channels & Synthesizing True Green...")
    R_norm = normalize_channel(R)
    B_norm = normalize_channel(B)
    G_veg_norm = normalize_channel(G_veg)

    G_norm = 0.45 * R_norm + 0.10 * G_veg_norm + 0.45 * B_norm
    G_norm = np.clip(G_norm, 0.0, 1.0)

    print("    Stacking channels into final RGB matrix...")
    rgb_image = np.stack([R_norm, G_norm, B_norm], axis=-1)

    h, w = rgb_image.shape[:2]
    if h > img_max_pixel:
        h = img_max_pixel
    if w > img_max_pixel:
        w = img_max_pixel

    rgb_image = cv2.resize(rgb_image, (w, h), interpolation=cv2.INTER_AREA)

    plt.imsave(output_path, rgb_image)
    print(f"      -> Successfully saved RGB composite with shape ({w} X {h}) to : {output_path}")

############################################################################################################################################################################

def single_channel_img_creater(file_path, output_image_path, color_map, img_max_pixel):
    print(f"    Reading: {os.path.basename(file_path)}")
    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        rad_array = ds['Rad'].values
        
    rad_array = np.nan_to_num(rad_array, nan=0.0)

    h, w = rad_array.shape[:2]
    if h > img_max_pixel:
        h = img_max_pixel
    if w > img_max_pixel:
        w = img_max_pixel
    rad_array = cv2.resize(rad_array, (w, h), interpolation=cv2.INTER_AREA)
    print(f"    Extracted image array with shape: ({w} X {h})")

    vmin = np.percentile(rad_array, 1)
    vmax = np.percentile(rad_array, 99)

    print(f"    Saving image (cmap: {color_map})...")
    plt.imsave(
        output_image_path, 
        rad_array, 
        vmin=vmin, 
        vmax=vmax, 
        cmap=color_map
    )
    print(f"      -> Successfully saved single channel image to: {output_image_path}")

############################################################################################################################################################################

def nc_imager(input_dir, output_dir, color_map, img_max_pixel, rgb_flag, chnl):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    Path(input_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    nc_files = list(Path(input_dir).rglob("*.nc"))
    if not nc_files:
        print(f"No .nc files found in the '{input_dir}' directory.")
        return

    timestamp_groups = {}
    all_detected_channels = set()
    
    for file_path in nc_files:
        channel = file_path.parent.name 
        filename = file_path.name
        timestamp_key = None
        for part in filename.split('_'):
            if part.startswith('s20'):
                timestamp_key = part
                break
        
        if channel.startswith('C') and timestamp_key:
            if timestamp_key not in timestamp_groups:
                timestamp_groups[timestamp_key] = {}
            timestamp_groups[timestamp_key][channel] = str(file_path)
            all_detected_channels.add(channel)

    rgb_timestamps = []
    for ts, channels in timestamp_groups.items():
        if 'C01' in channels and 'C02' in channels and 'C03' in channels:
            rgb_timestamps.append(ts)
            
    rgb_timestamps.sort()
    
    process_mode = "SINGLE"
    user_choice = None 
    if rgb_flag == None:
        print(f"Detected GOES-19 Data Channels : {sorted(list(all_detected_channels))}")
        
        if len(rgb_timestamps) > 0:
            if 'C01' and 'C02' and 'C03' in sorted(list(all_detected_channels)):
                print(f"\n[INFO] : Found all 3 channel sets capable of RGB rendering.")

            while True:
                user_choice = input("Do you want to render an (R)GB image or a (S)ingle channel? [R/S] : ").strip().upper()
                if user_choice in ['R', 'S']:
                    break
                print("\nInvalid input! Please enter exactly 'R' or 'S'.\n")
    
        if user_choice == 'R':
            process_mode = "RGB"

    elif rgb_flag == 'r' or rgb_flag == 'R':
        process_mode = "RGB"
    
    target_channel = "RGB_"

    if process_mode == "SINGLE" and chnl == None:
        print("\nSINGLE CHANNEL IMAGER :")
        ch_input = input("    -> Enter Channel Name or Number(e.g., C01, C13, 4, 14) : ").strip().upper()
        if ch_input not in all_detected_channels:
            padded = f"C{int(ch_input):02d}"
            if padded in all_detected_channels:
                target_channel = padded
            else:
                print(f"\n[ERROR] : Channel {ch_input} not found.")
                return
        else:
            target_channel = ch_input
    elif chnl != None and chnl != "RGB_":
        target_channel = f"C{chnl}"
                
    if process_mode == "RGB":
        valid_timestamps = rgb_timestamps
    else:
        valid_timestamps = [ts for ts, channels in timestamp_groups.items() if target_channel in channels]
        valid_timestamps.sort()

    if valid_timestamps:
        first_ts = valid_timestamps[0]
        last_ts = valid_timestamps[-1]

        if process_mode == "RGB":
            strt_tm_path = timestamp_groups[first_ts]['C01']
            end_tm_path = timestamp_groups[last_ts]['C01']
        else:
            strt_tm_path = timestamp_groups[first_ts][target_channel]
            end_tm_path = timestamp_groups[last_ts][target_channel]
        
        strt_tm_file = os.path.basename(strt_tm_path)
        end_tm_file = os.path.basename(end_tm_path)

        strt_tm = strt_tm_file[27:38]
        end_tm = end_tm_file[27:38]

        data_time = f"_s{strt_tm}_e{end_tm}"
    else:
        data_time = ""

    existing_pngs = glob.glob(os.path.join(output_dir, "[0-9]*.png"))
    frame_counter = max([int(os.path.basename(f).split('.')[0]) for f in existing_pngs] + [-1]) + 1

    for ts in valid_timestamps:
        output_filename = f"{frame_counter:05d}.png"
        output_image_path = os.path.join(output_dir, output_filename)
        print(f"\n>>> Creating {output_filename} (Data from: {ts})")
        
        if process_mode == "RGB":
            rgb_img_creater(timestamp_groups[ts], output_image_path, img_max_pixel)
        elif target_channel == 'C01':
            single_channel_img_creater(timestamp_groups[ts][target_channel], output_image_path, blue_cmap, img_max_pixel)
        elif target_channel == 'C02':
            single_channel_img_creater(timestamp_groups[ts][target_channel], output_image_path, red_cmap, img_max_pixel)
        elif target_channel == 'C03':
            single_channel_img_creater(timestamp_groups[ts][target_channel], output_image_path, green_cmap, img_max_pixel)
        elif target_channel == 'C13':
            single_channel_img_creater(timestamp_groups[ts][target_channel], output_image_path, color_map, img_max_pixel)
        else:
            single_channel_img_creater(timestamp_groups[ts][target_channel], output_image_path, None, img_max_pixel)
        frame_counter += 1
    print("\nImage Extraction Completed.")
    return user_choice, target_channel, data_time

############################################################################################################################################################################

def file_format_check(path, nc_folder_pattern):
    nc_entries = []
    png_files = []
    mp4_files = []

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if os.path.isfile(full_path):
            filename_lower = entry.lower()
            if filename_lower.endswith('.png'):
                png_files.append(entry)
            elif filename_lower.endswith('.mp4'):
                png_files.append(entry)

        elif os.path.isdir(full_path) and nc_folder_pattern.match(entry):
            nc_entries.append(entry)

    has_nc = len(nc_entries) > 0
    has_png = len(png_files) > 0
    has_mp4 = len(mp4_files) > 0

    existing_types_count = sum([has_nc, has_png, has_mp4])

    if existing_types_count > 1:
        print("\n" + "="*60)
        print(f"\n ERROR: Mixed file types detected in: '{path}'")
        print(f"   Strict Rule Broken: Only ONE type of file is allowed to exist.")
        print(f"   Current Detection status -> NC: {has_nc} | PNG: {has_png} | MP4: {has_mp4}")
        print("="*60 + "\n")
        return 
        
    elif existing_types_count == 0:
        print(f"\n WARNING: Folder '{path}' has no valid .nc, .png, or .mp4 files.")
        return 
    
    elif existing_types_count == 1:
        if has_nc:
            return nc_entries
        elif has_png:
            return png_files
        elif has_mp4:
            return mp4_files
        else: 
            pass

############################################################################################################################################################################

def img_to_video(img_folder_path, output_video_path, fps):
    images = [img for img in os.listdir(img_folder_path) if img.endswith(".png")]
    images.sort()

    if not images:
        print(f"\nNo images found in the directory {img_folder_path}.")
    else:
        first_image_path = os.path.join(img_folder_path, images[0])
        first_frame = cv2.imread(first_image_path)
        height, width, layers = first_frame.shape

        output_dir = os.path.dirname(output_video_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        print("\nWriting frames to video...")
        for img_name in images:
            img_path = os.path.join(img_folder_path, img_name)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()
        cv2.destroyAllWindows()
        print(f"     -> Success! Video saved as : {output_video_path}")

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
    channel = ""

    scale = 1
    if nc_flag == 1 or png_flag == 1:
        fps = int(input("\nWhat FPS do you want the original video to be (1, 15, 24, 30, 60, ...) ? \n     -> Enter : "))
        if nc_flag == 1:
            print("\n===============================================================================================================\n") # Extracting Images from .nc files....\n\n")
            RGB_flag, channel_ad, data_time_s_to_e = nc_imager(path, f"{rife_path}/input", c_map, nc_img_max_size, None, None)
            if channel_ad == "RGB_":
                channel_no = channel_ad
            else:
                channel_no = channel_ad[1:3]
                channel = f"C{channel_no}_"
            if img_output_flag == 'y':
                nc_imager(path,f"2.output/output{input_pointer}/Native_{channel}Images{data_time_s_to_e}" ,c_map, float('inf'), RGB_flag, channel_no)

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

            img_to_video(f"{rife_path}/input", f"{vid_output_path}/original_{channel}{int(fps)}fps{data_time_s_to_e}.mp4", int(fps))
            img_to_video(f"{rife_path}/vid_out", f"{vid_output_path}/final_{channel}{2**n}X_{int((2**n)*fps)}fps{data_time_s_to_e}.mp4", int((2**n)*fps))

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