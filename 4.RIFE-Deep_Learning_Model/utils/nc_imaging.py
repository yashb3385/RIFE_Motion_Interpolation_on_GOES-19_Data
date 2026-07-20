import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import shutil
import os
import cv2
import glob
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

blue_cmap = LinearSegmentedColormap.from_list("black_blue", ["black", "blue"])
green_cmap = LinearSegmentedColormap.from_list("black_green", ["black", "green"])
red_cmap = LinearSegmentedColormap.from_list("black_red", ["black", "red"])

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
    if rgb_flag == None and chnl == None:
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