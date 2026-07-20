import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap

blue_cmap = LinearSegmentedColormap.from_list("black_blue", ["black", "blue"])
green_cmap = LinearSegmentedColormap.from_list("black_green", ["black", "green"])
red_cmap = LinearSegmentedColormap.from_list("black_red", ["black", "red"])

def png_to_nc(input_folder, output_folder, start_time_str, end_time_str, color_map, chnl_no):
    if chnl_no == '01':
        color_map = blue_cmap
    elif chnl_no == '02':
        color_map = red_cmap
    elif chnl_no == '03':
        color_map = green_cmap
    else:
        pass
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Prepare Colormap Lookup
    print(f"\nProceeding to create .nc output....\n")
    cmap = plt.get_cmap(color_map)
    scalars = np.linspace(0, 1, 1024)
    cmap_colors = cmap(scalars)[:, :3]
    tree = KDTree(cmap_colors)

    start_dt = datetime.strptime(start_time_str, "%Y%j%H%M")
    end_dt = datetime.strptime(end_time_str, "%Y%j%H%M")
    png_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.png')], 
                       key=lambda x: int(os.path.splitext(x)[0]))
    num_files = len(png_files)
    interval = (end_dt - start_dt) / (num_files - 1) if num_files > 1 else 0
    c_str = datetime.now().strftime("%Y%j%H%M") + "573"

    for i, png_file in enumerate(png_files):
        # Load and Prepare Image
        img = plt.imread(os.path.join(input_folder, png_file))
        if img.shape[-1] == 4: img = img[:, :, :3]
        if img.max() > 2.0: img = img / 255.0
        
        # KDTree Mapping
        flat_img = img.reshape(-1, 3)
        _, indices = tree.query(flat_img)
        pseudo_rad = scalars[indices].reshape(img.shape[0], img.shape[1])
        
        current_s_dt = start_dt + (interval * i)
        current_e_dt = start_dt + (interval * (i+1)) - timedelta(minutes=1)
        s_str = current_s_dt.strftime("%Y%j%H%M") + "000"
        e_str = current_e_dt.strftime("%Y%j%H%M") + "000"
        
        ds = xr.Dataset({"Rad": (["y", "x"], pseudo_rad.astype(np.float32))})
        filename = f"OR_ABI-L1b-RadF-M6C13_G19_s{s_str}_e{e_str}_c{c_str}.nc"
        ds.to_netcdf(os.path.join(output_folder, filename))
        print(f"Processed : {png_file} -> {filename}")

# png_to_nc("input", "output", "20250010000", "20250010130", "RdYlBu_r")