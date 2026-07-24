# Mean Squared Error (MSE)
**Mean Squared Error (MSE)** measures the average squared difference between an original reference signal (or image) and a processed, noisy, or reconstructed version. It quantifies the cumulative error magnitude, where lower values indicate higher similarity to the original.
## Formula

$$\text{MSE} = \frac{1}{m \cdot n} \sum_{i=0}^{m-1} \sum_{j=0}^{n-1} [I(i,j) - K(i,j)]^2$$

### Terms Used in the Formula
- $m$ ➔ Total number of rows (image height in pixels).

- $n$ ➔ Total number of columns (image width in pixels).

- $m \cdot n$ ➔ Total count of pixels (data points) in the grid.

- $i$ ➔ Row index variable, looping from $0$ to $m-1$.

- $j$ ➔ Column index variable, looping from $0$ to $n-1$.

- $I(i,j)$ ➔ Pixel intensity value at coordinate $(i, j)$ in the **original/reference** image $I$.

- $K(i,j)$ ➔ Pixel intensity value at coordinate $(i, j)$ in the **degraded/reconstructed** image $K$.
# Peak Signal-to-Noise Ratio (PSNR)
**Peak Signal-to-Noise Ratio (PSNR)** evaluates signal fidelity by taking the ratio of the maximum possible signal power to the corrupting noise power. Expressed on a logarithmic decibel ($\text{dB}$) scale, higher PSNR values indicate higher image quality and lower reconstruction noise.
## Formula
$$\text{PSNR} = 10 \cdot \log_{10} \left( \frac{\text{MAX}_I^2}{\text{MSE}} \right)$$
### Terms Used in the Formula
- $\text{PSNR}$ ➔ Peak Signal-to-Noise Ratio (measured in $\text{dB}$).

- $\text{MAX}_I$ ➔ The maximum possible signal value (dynamic range):
    
    - For an ***8-bit image*** ➔ $\text{MAX}_I = 2^8 - 1 = 255$
        
    - For a ***16-bit image*** ➔ $\text{MAX}_I = 2^{16} - 1 = 65,535$
        
    - For ***normalized data*** ➔ $\text{MAX}_I = 1.0$

- $\text{MSE}$ ➔ Mean Squared Error between the reference and reconstructed images.
