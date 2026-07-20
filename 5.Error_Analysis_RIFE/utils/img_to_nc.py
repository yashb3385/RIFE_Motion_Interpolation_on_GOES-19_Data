import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from datetime import datetime
from matplotlib.colors import LinearSegmentedColormap

blue_cmap = LinearSegmentedColormap.from_list("black_blue", ["black", "blue"])
green_cmap = LinearSegmentedColormap.from_list("black_green", ["black", "green"])
red_cmap = LinearSegmentedColormap.from_list("black_red", ["black", "red"])

def png_to_inter_nc(image_path, output_folder, file_name, color_map, chnl_no):
    if chnl_no == '01':
        color_map = blue_cmap
    elif chnl_no == '02':
        color_map = red_cmap
    elif chnl_no == '03':
        color_map = green_cmap
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"\nProceeding to create .nc output....\n")
    
    # Prepare Colormap Lookup
    cmap = plt.get_cmap(color_map)
    scalars = np.linspace(0, 1, 1024)
    cmap_colors = cmap(scalars)[:, :3]
    tree = KDTree(cmap_colors)

    # Load and Prepare Image
    img = plt.imread(image_path)
    if img.shape[-1] == 4: img = img[:, :, :3]
    if img.max() > 2.0: img = img / 255.0
    
    # KDTree Mapping
    flat_img = img.reshape(-1, 3)
    _, indices = tree.query(flat_img)
    pseudo_rad = scalars[indices].reshape(img.shape[0], img.shape[1])
    
    ds = xr.Dataset({"Rad": (["y", "x"], pseudo_rad.astype(np.float32))})
    filename = f"{file_name[:-3]}_inter.nc"
    
    out_path = os.path.join(output_folder, filename)
    ds.to_netcdf(out_path)
    
    print(f"Processed : {os.path.basename(image_path)} -> {filename}")

# png_to_nc_single("input/1.png", "output", "20250010000", "20250010029", "RdYlBu_r", "13")