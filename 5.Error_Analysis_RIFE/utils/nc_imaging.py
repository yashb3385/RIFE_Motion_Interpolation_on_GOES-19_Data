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
    print(f"      -> Successfully saved single channel image to : {output_image_path}")

############################################################################################################################################################################

def nc_imager(input_dir, output_dir, color_map, img_max_pixel, chnl):
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
    
    target_channel = ""

    if chnl == None:
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
    elif chnl != None:
        target_channel = f"C{chnl}"
                
    valid_timestamps = [ts for ts, channels in timestamp_groups.items() if target_channel in channels]
    valid_timestamps.sort()

    existing_pngs = glob.glob(os.path.join(output_dir, "[0-9]*.png"))
    frame_counter = max([int(os.path.basename(f).split('.')[0]) for f in existing_pngs] + [-1]) + 1

    for ts in valid_timestamps:
        output_filename = f"{frame_counter:05d}.png"
        output_image_path = os.path.join(output_dir, output_filename)
        print(f"\n>>> Creating {output_filename} (Data from: {ts})")
        
        if target_channel == 'C01':
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
    return target_channel