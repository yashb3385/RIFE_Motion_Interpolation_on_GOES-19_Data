import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


file_c01 = "input/OR_ABI-L1b-RadF-M6C01_G19_s20242841950203_e20242841959511_c20242841959546.nc"  # Blue
file_c02 = "input/OR_ABI-L1b-RadF-M6C02_G19_s20242841950203_e20242841959511_c20242841959540.nc"  # Red
file_c03 = "input/OR_ABI-L1b-RadF-M6C03_G19_s20242841950203_e20242841959511_c20242841959550.nc"  # Veggie (Near-IR)

output_image_path = "output/image.png"

def load_and_clean(file_path):
    """Opens a single .nc file, extracts radiance, and cleans NaNs."""
    print(f"Reading: {file_path}")
    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        data = ds['Rad'].values
    return np.nan_to_num(data, nan=0.0)

print("Opening NetCDF files...")
R = load_and_clean(file_c02)
B = load_and_clean(file_c01)
G_veg = load_and_clean(file_c03)

# Resolution Matching Safety Check
# On GOES satellites, Channel 2 (Red) is high-res (0.5km), while Ch 1 & 3 are lower-res (1km).
# If the dimensions don't match, we downsample the Red channel by taking every 2nd pixel.
if R.shape != B.shape:
    print(f"Shape mismatch detected! Adjusting Red channel resolution {R.shape} to match Blue channel {B.shape}...")
    R = R[::2, ::2]

# Normalize function using the 1st and 99th percentiles
def normalize_channel(band_array):
    vmin = np.percentile(band_array, 1)
    vmax = np.percentile(band_array, 99)
    # Clip extreme values and scale strictly between 0.0 and 1.0
    clipped = np.clip(band_array, vmin, vmax)
    return (clipped - vmin) / (vmax - vmin)

print("Normalizing individual channels...")
R_norm = normalize_channel(R)
B_norm = normalize_channel(B)
G_veg_norm = normalize_channel(G_veg)

# Generate the Synthetic True Green Channel
# Formula maps Red, Blue, and Near-Infrared to simulate human eye green perception
print("Synthesizing true green channel...")
G_norm = 0.45 * R_norm + 0.10 * G_veg_norm + 0.45 * B_norm
G_norm = np.clip(G_norm, 0.0, 1.0)

# 6. Stack the matrices together into a single RGB image array
# Shape transforms from individual (5424, 5424) arrays into one (5424, 5424, 3) array
print("Stacking channels into final RGB matrix...")
rgb_image = np.stack([R_norm, G_norm, B_norm], axis=-1)

# 7. Save the final multi-color composite image
print(f"Saving multi-color image to {output_image_path}...")
plt.imsave(output_image_path, rgb_image)

print("Process complete! Successfully generated true color image.")