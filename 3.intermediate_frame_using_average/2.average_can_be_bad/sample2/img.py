import cv2
import numpy as np

def png_intermediate(png1_path, png2_path, png_inter_path):
    # Load images with IMREAD_UNCHANGED to keep all channels (including Alpha/PNG transparency)
    img1 = cv2.imread(png1_path, cv2.IMREAD_UNCHANGED)
    img2 = cv2.imread(png2_path, cv2.IMREAD_UNCHANGED)

    # Ensure both image arrays are the exact same size
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convert to 16-bit integers to prevent 8-bit overflow during addition
    img1_16 = img1.astype(np.uint16)
    img2_16 = img2.astype(np.uint16)

    # Take the absolute integer average (exactly like integer math in C)
    # Using '//' ensures C-style floor integer division
    average_16 = (img1_16 + img2_16) // 2

    # Cast back down to standard 8-bit image format with zero post-processing
    final_img = average_16.astype(np.uint8)

    # Save the output PNG
    cv2.imwrite(png_inter_path, final_img)

png1_path = '0.png'
png2_path = '2.png'
png_inter = '1_inter.png'