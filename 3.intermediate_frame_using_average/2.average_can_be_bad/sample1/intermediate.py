import xarray as xr
import shutil

def intermediate(file_frame_a, file_frame_b, output_interp_file):
    print("Loading original NetCDF files...")
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


    # Export back out to a physical scientific .nc file
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

    print("Saved successfully!")

    # Close the open file handlers cleanly to free system RAM
    ds_a.close()
    ds_b.close()
    ds_intermediate.close()

    print("Process complete! The intermediate .nc file has been successfully generated.")

for i in range(3):
    intermediate(f"input/{2*i}.nc", f"input/{2*(i+1)}.nc", f"output/{(2*i)+1}.nc")
    shutil.copy2(f"input/{2*i}.nc", "output")
shutil.copy2("input/6.nc", "output")