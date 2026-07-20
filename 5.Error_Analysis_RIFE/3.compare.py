import xarray as xr
import numpy as np
import cv2
import os
from skimage.metrics import mean_squared_error, peak_signal_noise_ratio, structural_similarity
from utils.fsim import calculate_fsim_native
from utils.error_plot import plot_spatial_errors
from utils.get_channel_inter import get_channel_inter_file

def calculate_nc_metrics(real_nc_path, interpolated_nc_path, chnl, time):

    print(f"\nOpening Real File : {real_nc_path}")
    ds_real = xr.open_dataset(real_nc_path)
    
    print(f"\nOpening Interpolated File : {interpolated_nc_path}")
    ds_interp = xr.open_dataset(interpolated_nc_path)

    try:
        # Extract 2D scientific telemetry arrays
        grid_real = ds_real['Rad'].values
        grid_interp = ds_interp['Rad'].values
    except KeyError:
        print("\n[ERROR] : Could not find the variable 'Rad' in one of the datasets.")
        return None
    finally:
        ds_real.close()
        ds_interp.close()

    # RESOLUTION MISMATCH & MEMORY CONTROL
    if grid_real.shape != grid_interp.shape:
        print(f"\n[!] Resolution mismatch detected!")
        print(f"   -> Large Real File Shape  : {grid_real.shape}")
        print(f"   -> Model Output Shape     : {grid_interp.shape}")
        print(f"\n[INFO] : Downscaling real matrix to match model output size...")
        
        target_width = grid_interp.shape[1]  
        target_height = grid_interp.shape[0] 
        
        # INTER_AREA provides clean spatial downscaling without introducing artifact noise
        grid_real = cv2.resize(grid_real, (target_width, target_height), interpolation=cv2.INTER_AREA)
        print("   -> Successfully downscaled real file.")

    # Clean missing/null telemetry entries safely
    grid_real = np.nan_to_num(grid_real, nan=0.0)
    grid_interp = np.nan_to_num(grid_interp, nan=0.0)

    # Dynamic Min-Max Normalization to protect error baselines from scale shifts
    min_real, max_real = grid_real.min(), grid_real.max()
    min_interp, max_interp = grid_interp.min(), grid_interp.max()

    real_norm = (grid_real - min_real) / (max_real - min_real) if max_real != min_real else np.zeros_like(grid_real)
    interp_norm = (grid_interp - min_interp) / (max_interp - min_interp) if max_interp != min_interp else np.zeros_like(grid_interp)

    # Computing error metrics
    mse_val = mean_squared_error(real_norm, interp_norm)
    psnr_val = peak_signal_noise_ratio(real_norm, interp_norm, data_range=1.0)
    ssim_val = structural_similarity(real_norm, interp_norm, data_range=1.0)
    fsim_val = calculate_fsim_native(real_norm, interp_norm)

    # Display Dashboard
    print("\n" + "="*59)
    print("             SATELLITE NETCDF ERROR DASHBOARD        ")
    print(f"                   (Time : {time})     ")
    print("="*59)
    print(f"  Mean Squared Error    (MSE)    :   {mse_val:.6f}")
    print(f"  Peak Signal-to-Noise  (PSNR)   :   {psnr_val:.2f} dB")
    print(f"  Structural Sim        (SSIM)   :   {ssim_val:.4f}")
    print(f"  Feature Similarity    (FSIM)   :   {fsim_val:.4f}")
    print("="*59 + "\n")

    # Export diagnostic visualization
    plot_spatial_errors(real_norm, interp_norm, mse_val, ssim_val, chnl, time)

    return mse_val, psnr_val, ssim_val, fsim_val

channels = input("\nEnter the Channel Numbers separated by spaces for error calculation : ")
channels_list = [int(i) for i in channels.split()]

for i in channels_list:
    real_file, generated_file = get_channel_inter_file(i, "intermediate")
    time = (os.path.basename(real_file))[27:38]
    print("\n\n===============================================================================================================")
    print("===============================================================================================================")
    print(f"                               Error Analysis ( Channel : {i:02d} , Time : {time} )")
    print("===============================================================================================================")
    print("===============================================================================================================")
    calculate_nc_metrics(real_file, generated_file, i, time)