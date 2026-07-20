import cv2
import numpy as np

def calculate_fsim_native(org_grid, pred_grid):

    # Ensure inputs are 64-bit floats for high-precision scientific evaluation
    org_gray = org_grid.astype(np.float64)
    pred_gray = pred_grid.astype(np.float64)

    # Gradient Magnitude (GM) tracking using Sobel spatial filters
    dx_org = cv2.Sobel(org_gray, cv2.CV_64F, 1, 0, ksize=3)
    dy_org = cv2.Sobel(org_gray, cv2.CV_64F, 0, 1, ksize=3)
    gm_org = np.sqrt(dx_org**2 + dy_org**2)

    dx_pred = cv2.Sobel(pred_gray, cv2.CV_64F, 1, 0, ksize=3)
    dy_pred = cv2.Sobel(pred_gray, cv2.CV_64F, 0, 1, ksize=3)
    gm_pred = np.sqrt(dx_pred**2 + dy_pred**2)

    # Phase Congruency (PC) structural features via Laplacian filter
    pc_org = np.abs(cv2.Laplacian(org_gray, cv2.CV_64F))
    pc_pred = np.abs(cv2.Laplacian(pred_gray, cv2.CV_64F))

    # Stability constants from original FSIM documentation
    T1, T2 = 0.85, 160.0 

    # Calculate individual similarity mapping layers
    S_pc = (2 * pc_org * pc_pred + T1) / (pc_org**2 + pc_pred**2 + T1)
    S_gm = (2 * gm_org * gm_pred + T2) / (gm_org**2 + gm_pred**2 + T2)

    # Compound spatial score matrix
    S_x = S_pc * S_gm
    
    # Weigh the total map score using maximum structural prominence
    PC_max = np.maximum(pc_org, pc_pred)
    
    # Handle edge case for completely blank/zeroed regions to avoid Division-by-Zero
    if np.sum(PC_max) == 0:
        return 1.0
        
    return np.sum(S_x * PC_max) / np.sum(PC_max)