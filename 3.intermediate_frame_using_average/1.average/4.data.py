import xarray as xr

def nc_reader(file):
    ds = xr.open_dataset(file)

    # Inspecting the file structure
    # This prints the variables, coordinates, and metadata
    print(f"\n\n##########################################################################################################################")
    print(f"######### Dataset Metadata ({file[18:21]}-Intr), Time : {file[34:36]}-{file[36:38]}-{file[38:40]}, Year : {file[27:31]}, Day : {file[31:34]} ###########################################") if "intr" in file else print(f"######### Dataset Metadata ({file[18:21]}), Time : {file[34:36]}-{file[36:38]}-{file[38:40]}, Year : {file[27:31]}, Day : {file[31:34]} ################################################")
    print(f"##########################################################################################################################\n\n")
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
        print(f"\nSuccessfully extracted data with shape: {data_array.shape}\n\n\n")

    except KeyError:
        print("Variable 'Rad' not found. Check the printed dataset metadata for correct variable names.\n\n\n")

    ds.close()

file_a = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242842000203_e20242842009523_c20242842009570.nc"
file_b = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242842010203_e20242842019523_c20242842019576.nc"
file_c = "input/OR_ABI-L1b-RadF-M6C13_G19_s20242842020203_e20242842029523_c20242842029562.nc"
file_intr = "output/OR_ABI-L1b-RadF-M6C13_G19_s20242842010000_intr.nc"

nc_reader(file_intr)
nc_reader(file_b)