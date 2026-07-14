import xarray as xr

# 1. Define paths to your two consecutive snapshots
file_frame_a = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242842000203_e20242842009523_c20242842009570.nc"  # Time T
file_frame_b = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242842020203_e20242842029523_c20242842029562.nc"  # Time T + 10 mins
output_interp_file = "output/OR_ABI-L1b-RadF-M6C13_G19_s20242842010000_intr.nc"               # Target synthesized frame

print("\nLoading original NetCDF files...")
# Open datasets using xarray
ds_a = xr.open_dataset(file_frame_a, engine="netcdf4")
ds_b = xr.open_dataset(file_frame_b, engine="netcdf4")

print("Generating intermediate dataset structure...")
# Deep copy the first dataset. This copies all global attributes, projections,
# data dimensions, and coordinate definitions safely.
ds_intermediate = ds_a.copy(deep=True)

print("Calculating pixel-wise radiance average...")
# Direct element-wise matrix addition and division. 
# xarray aligns the coordinates automatically before doing the math.
averaged_radiance = (ds_a['Rad'] + ds_b['Rad']) / 2.0

# Replace any unexpected NaN anomalies with a baseline value
ds_intermediate['Rad'] = averaged_radiance.fillna(0.0)

print("Updating the internal observation timestamp...")
# Extract the underlying numpy datetime64 timestamps
t_a = ds_a['t'].values
t_b = ds_b['t'].values

# Calculate the exact midpoint in time
midpoint_timestamp = t_a + (t_b - t_a) / 2
print(f"Frame A Time: {t_a}")
print(f"Frame B Time: {t_b}")
print(f"Synthesized Midpoint Time: {midpoint_timestamp}")

# Assign the updated timestamp coordinate back into the new dataset template
ds_intermediate = ds_intermediate.assign_coords(t=midpoint_timestamp)

# 5. Export back out to a physical scientific .nc file on your Zorin OS system
print(f"Writing output file to disk: {output_interp_file}...")
ds_intermediate.to_netcdf(output_interp_file, engine="netcdf4")


# Clear out the old sensor encoding so it doesn't conflict with our new averaged values
if 'Rad' in ds_intermediate.variables:
    ds_intermediate['Rad'].encoding.clear()

# Define clean encoding settings (adds zlib compression to keep file size small)
encoding_settings = {
    'Rad': {
        'zlib': True,          # Turn on compression
        'complevel': 4,        # Compression level (1-9)
        'dtype': 'float32'     # Save it as clean 32-bit floating numbers
    }
}

print(f"Writing fully georeferenced NetCDF file to: {output_interp_file}...")

# Save the dataset with our custom encoding map
ds_intermediate.to_netcdf(
    output_interp_file, 
    engine="netcdf4", 
    encoding=encoding_settings
)

# Close the open file handlers cleanly to free system RAM
ds_a.close()
ds_b.close()
ds_intermediate.close()

print("\nProcess complete! The intermediate .nc file has been successfully generated.")
print(f"   -> Saved successfully to path : {output_interp_file}\n")