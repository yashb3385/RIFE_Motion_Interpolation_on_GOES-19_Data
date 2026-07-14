import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

def image_creater(file_path):
    # Can change extension to .jpg
    output_image_path = f"img_output/{file_path[7:8]}.png"
    print("Opening NetCDF file...")
    with xr.open_dataset(file_path, engine="netcdf4") as ds:
        
        # Extract the Radiance array
        # 'Rad' dimension is (y: 5424, x: 5424) as seen in metadata
        rad_array = ds['Rad'].values
        
        print(f"Extracted image array with shape: {rad_array.shape}")

    # Clean and preprocess data
    # Replace NaN values or bad data flags with 0 to prevent rendering errors
    rad_array = np.nan_to_num(rad_array, nan=0.0)

    # Filter extreme noise outliers for better visual contrast
    # We use percentiles (e.g., 1st and 99th) instead of strict min/max
    vmin = np.percentile(rad_array, 1)
    vmax = np.percentile(rad_array, 99)

    # vmin = np.percentile(rad_array, 1)
    # This tells Python to sort all 29 million pixels (5424 × 5424) from lowest to highest radiance,
    # and find the value at the 1st percentile mark. 

    # Any pixel value lower than this (like deep space noise) 
    # is ignored and clamped to this floor value.

    # vmax = np.percentile(rad_array, 99)
    # This finds the value at the 99th percentile mark. 

    # Any pixel value higher than this (like a hot sensor glitch or highly reflective anomaly) 
    # is ignored and clamped to this ceiling value.


    print("Saving image...")
    # Note on 'cmap': 
    # 'gray' provides normal grayscale.
    # 'gray_r' provides inverted grayscale (standard for thermal satellite imagery).
    # 'turbo', 'jet', 'RdYlBu_r', etc. also can be used for colored mapping.
    plt.imsave(
        output_image_path, 
        rad_array, 
        vmin=vmin, 
        vmax=vmax, 
        cmap='gray'
    )

    print(f"Successfully saved image to: {output_image_path}")
for i in range(3):
    image_creater(f"output/{2*i}.nc")
    image_creater(f"output/{(2*i)+1}_inter.nc")
image_creater("output/6.nc")