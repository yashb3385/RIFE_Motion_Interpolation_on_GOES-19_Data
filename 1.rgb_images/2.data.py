import xarray as xr

file_c01 = "input/OR_ABI-L1b-RadF-M6C01_G19_s20242841950203_e20242841959511_c20242841959546.nc"  # Blue
file_c02 = "input/OR_ABI-L1b-RadF-M6C02_G19_s20242841950203_e20242841959511_c20242841959540.nc"  # Red
file_c03 = "input/OR_ABI-L1b-RadF-M6C03_G19_s20242841950203_e20242841959511_c20242841959550.nc"  # Veggie (Near-IR)

def nc_reader(file):
    ds = xr.open_dataset(file)

    # Inspecting the file structure
    # This prints the variables, coordinates, and metadata
    print(f"\n\n##########################################################################################################################")
    print(f"################# Dataset Metadata ({file[18:21]}) #################################################################################")
    print(f"##########################################################################################################################\n\n")
    print(ds)

    # For GOES-19/INSAT, the data is usually stored under the variable name 'Rad'
    try:
        rad_data = ds['Rad']
        print("\n\n--------- Variable Info --------------------------------------------------------------------------------------------\n\n")
        print(f"Shape: {rad_data.shape}")
        print(f"Coordinates: {rad_data.coords}")
        
        data_array = rad_data.values
        print(f"\nSuccessfully extracted data with shape: {data_array.shape}\n\n\n")

    except KeyError:
        print("Variable 'Rad' not found. Check the printed dataset metadata for correct variable names.\n\n\n")

    ds.close()

nc_reader(file_c01)
nc_reader(file_c02)
nc_reader(file_c03)