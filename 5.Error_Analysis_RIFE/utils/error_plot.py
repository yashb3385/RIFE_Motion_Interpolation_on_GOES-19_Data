import matplotlib.pyplot as plt
import numpy as np

def plot_spatial_errors(real_arr, interp_arr, mse, ssim, channel_no, time):
    error_map = np.abs(real_arr - interp_arr)
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Real Ground Truth (Downscaled)")
    plt.imshow(real_arr, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("AI Interpolated")
    plt.imshow(interp_arr, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title(f"Spatial Error Matrix\n(MSE: {mse:.5f} | SSIM: {ssim:.3f})")
    plt.imshow(error_map, cmap='inferno')
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.axis('off')
    
    plt.tight_layout()

    plot_name = f"C{int(channel_no):02d}_error_{time}.png"

    plt.savefig(plot_name, dpi=300)
    print(f"[INFO] : Error visualization saved as {plot_name}\n")
    plt.close()