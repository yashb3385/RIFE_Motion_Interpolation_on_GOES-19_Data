**FSIM** (Feature Similarity Index) is an advanced full-reference ***Image Quality Assessment (IQA)*** metric designed to evaluate the visual quality of an image by comparing it to a reference image. It was created to closely align with how the ***Human Visual System (HVS)*** perceives image quality degradation.
# What It Actually Does
Unlike older metrics like MSE (Mean Squared Error) or PSNR, which simply compare pixel-by-pixel differences, FSIM evaluates an image based on low-level human visual perception features. Specifically, it performs the following steps:
## 1. Extracts Structural and Detail Features
- **Phase Congruency (PC)** ➔ Measures structural significance across multiple scales and orientations, remaining invariant to changes in image illumination and contrast.

- **Gradient Magnitude (GM)** ➔ Detects edges, sharpness, and fine details using derivative operators.
## 2. Computes Local Similarities 
- It compares the PC and GM maps of the reference image and the distorted/processed image to generate local similarity maps.

- If evaluated using its color extension ($\text{FSIM}_c$), it also computes chromaticity similarity using color-opponent channels (such as $YIQ$) to account for color distortions.        
## 3. Pools Features Using Perceptual Weighting
- Instead of averaging all pixels equally, it uses **Phase Congruency** as a weight. Areas containing important structures and edges carry more weight in the final score than flat, uniform backgrounds, because human eyes are more sensitive to structural changes in salient regions.
## 4. Outputs a Final Score
- It produces a single scalar score (typically between 0 and 1, where 1 indicates identical quality) representing the perceptual similarity between the two images.
# Calculation Method Flow Chart
![](FSIM.png)
## Formula
$$\Huge\Huge{FSIM=\frac{\sum\limits_{X\in\ohm}S_L(X).PC_m(X)}{\sum\limits_{X\in\ohm}PC_m(X)}}$$
### Frequency Domain Transfer Function of *2D LOG-Gabor Filter*
$$\huge{G_{n,o}(\omega,\theta)=e^{\frac{-(\ln(\frac{\omega}{\omega_n}))^2}{2(\ln(\frac{\sigma_f}{\omega_n}))^2}}.e^{\frac{-(\theta-\theta_o)^2}{2\sigma_{\theta}^2}}}$$
### Terminologies
- $S_L$ ➔ **Combined Local Similarity**.

- $PC_m$ ➔ **Maximum Phase Congruency Map**.

- $I_i$  ➔ *Image Matrix* of $i^{th}$ image.

- $n$ ➔ *Filter Scale* / *Frequency Scale* ( Here, $n\in\{1,2,3,4\}$ ).

- $N$ ➔ Total No. of scales ( Here, $N=4$ ).

- $o$ ➔ *Filter Orientation* ( $o\in\{1,2,3,4,5,6\}$ ).

- $W,H$ ➔ *Width* & *Height* of the image.

- $x$ ➔ *Column Index* of image ( $x\in\{0,1,2,...,W-1\}$ ).

- $y$ ➔ *Row Index* of image ( $x\in\{0,1,2,...,H-1\}$ ).

- $\sigma_r$ ➔ *Scale Parameter*.

- $\mu_o$ ➔ *Mean Noise Energy*.

- $k$ ➔ *Constant Multiplier* ( Usually $2$ or $3$ ).

- $\sigma_o$ ➔ *Standard Deviation of Noise*.

- $\epsilon$ ➔ *Stability Constant* ( Preferably $0.0001$ to prevent division by zero ).

- $\omega$ ➔ *Radial Frequency*.

- $\theta$ ➔ *Angular Coordinate*.

- $\delta$ ➔ *Scaling Factor* ( Typically $0.5$ ).

- $\sigma_f$ ➔ *Frequency Standard Deviation*.

- $\sigma_\theta$ ➔ *Angular Standard Deviation* ( Typically optimized to $0.35$ $radians$ ).

- $T_1$ ➔ *Phase Congruency Stability Constant* ( Value optimized to $0.85$ ).

- $T_2$ ➔ *Gradient Magnitude Stability Constant* ( Value optimized to $160$ ).

- $k_x,k_y$ ➔ *Kernel Matrices*.
