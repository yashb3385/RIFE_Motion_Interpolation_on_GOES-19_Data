import xarray as xr

file_path = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242841950203_e20242841959523_c20242841959578.nc"
ds = xr.open_dataset(file_path)

# Inspecting the file structure
# This prints the variables, coordinates, and metadata
print("\n\n--------- Dataset Metadata -----------------------------------------------------------------------------------------\n\n")
print(ds)

# For GOES-19/INSAT, the data is usually stored under the variable name 'Rad'
# You can verify the exact name by looking at the print(ds) output
try:
    rad_data = ds['Rad']
    print("\n\n--------- Variable Info --------------------------------------------------------------------------------------------\n\n")
    print(f"Shape: {rad_data.shape}")
    print(f"Coordinates: {rad_data.coords}")
    
    # 4. Extract data as a numpy array for your AI model
    # The .values attribute converts the xarray DataArray to a raw numpy array
    data_array = rad_data.values
    print(f"\nSuccessfully extracted data with shape: {data_array.shape}")

except KeyError:
    print("Variable 'Rad' not found. Check the printed dataset metadata for correct variable names.")

ds.close()
