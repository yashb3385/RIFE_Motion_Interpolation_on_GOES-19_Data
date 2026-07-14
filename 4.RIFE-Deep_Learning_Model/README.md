# Fill in the Frames Seamlessly - Enhancing Temporal Resolution of Satellite Imagery using AI/ML
---
## Introduction
---
Satellite images from geostationary satellites are often captured at fixed intervals (e.g., every 30 minutes for INSAT, or every 10 minutes for Himawari/GOES). This restricts near real-time monitoring of dynamic and fast-moving phenomena such as cyclones, thunderstorms, floods, and rapid land changes. Traditional optical-flow temporal interpolation methods are limited, often yielding incorrect results like blurred images and artifacts, failing to capture non-linear cloud dynamics. 

![Alt Text](ECCV2022-RIFE/demo/SAT.jpg)

This project develops and uses an AI/ML-based Optical Flow frame interpolation technique to generate synthetic intermediate frames between consecutive satellite images. This effectively enhances temporal resolution (e.g., from 10 minutes to 5 or 2.5 minutes), enabling more frequent observations without requiring additional satellite resources.
## Dataset Links
---
### GOES-19 ABI Channel 13 data from NOAA GOES-19 AWS bucket
- [NOAA-GOES-19 Link](https://noaa-goes19.s3.amazonaws.com/index.html)
$\hspace{1cm}$
- [NOAA-GOES-19 ABI-L1b-RadF Link](https://noaa-goes19.s3.amazonaws.com/index.html#ABI-L1b-RadF/)
### INSAT-3DS/3DR TIR1 channel data from mosdac
- [INSAT-3DR Link](https://mosdac.gov.in/catalog-app/satellite?mission=INSAT-3DR)
$\hspace{1cm}$
- [INSAT-3DS Link](https://mosdac.gov.in/catalog-app/satellite?mission=INSAT-3DS)
## Dataset Used
---
This project utilizes satellite imagery obtained from the ***NOAA GOES-19*** AWS bucket ([NOAA-GOES-19 ABI-L1b-RadF](https://noaa-goes19.s3.amazonaws.com/index.html#ABI-L1b-RadF/)). The data utilized includes: 
$\hspace{1cm}$
* **True-Color RGB Composition** $\boldsymbol{\to}$ Constructed using Channels 1, 2, and 3: 
	1. *Blue* : Channel 1 
	2. *Red* : Channel 2 
	3. *Green* : Channel 3 
$\hspace{1cm}$
* **Thermal Imaging** $\boldsymbol{\to}$ Derived from *Channel 13*, which actually contains ***Thermal Infrared band data*** (~10 $\mu m$).
## 📂 Repository Usage Guide
---
*   **Execution Order** $\boldsymbol{\to}$ All Python scripts are prefixed with a number (e.g., `1.xyz.py`, `2.xyz.py`). It will be preferable to execute them in ascending numerical order.
$\hspace{1cm}$
*   **Utility Scripts** $\boldsymbol{\to}$ Every folder contains a `download.py` and a `delete.py` (specially input folders) to manage fetching necessary input data and cleaning up outputs.
## Deep Learning Interpolation (4.RIFE-Deep_Learning_Model)
---

This directory contains the core solution of the project : the prebuilt [**ECCV2022-RIFE**](https://github.com/hzwer/ECCV2022-RIFE) deep learning model developed by [hzwer](https://github.com/hzwer). RIFE (***Real-Time Intermediate Flow Estimation***) accurately calculates optical flow to synthesize completely new, physically plausible frames between satellite captures. Here is Step-by-Step Execution:
### 1. Setup and Installation
Execute **1.install_requirements.py** to download and install all necessary dependencies, weights, and libraries for the RIFE model. 
```bash
python 1.install_requirements.py
```

>**Note** $\boldsymbol{\to}$ This installation is heavy and will consume approximately ***10 GB*** of disk space. This will install ***Python 3.10*** as virtual environment all heavy packages will be installed for Python 3.10.
### 2. Preparing the Input Data
Before running the model, you must place your data into the input directories located at `1.input/input1`, `1.input/input2`, etc. The RIFE model pipeline is highly versatile and accepts:
*   Standard image frames (`.png`)
*   Video files (`.mp4`)
*   Raw satellite data (`.nc` files) in their respective channel folders.

> ***Note*** $\boldsymbol\to$ All input folders contain `1.download.py` and `2.delete.py` to download sample input data except `1.input/input4` as it contains scripts `1.download.py` and `2.delete.py` to download and clean **actual GOES-19 data**.

**Handling `.nc` Files :**

- You can place raw `.nc` files inside their respective `C{i}` Channel Folders (e.g.`C01, C03, C13,etc.`) within the input directories. 
$\hspace{1cm}$
- For convenience, you can *automatically download* required `.nc` files directly into `1.input/input4` using the included `1.download.py` utility.
$\hspace{1cm}$
- **`2.delete.py`** $\boldsymbol{\to}$ Safely deletes the all channel folders where your `.nc` files in your input directory. This file must be placed in the input directory. You can find it in `1.input/input4`.
### 3. Executing the Interpolation Model
Once your inputs are staged, run:
```bash
python 2.executer.py
```
### 4. Managing Storage & Cleanup
Because satellite data and model dependencies take up significant space, robust cleanup tools are provided:

- **`2.delete.py`** $\boldsymbol{\to}$ Safely deletes the all channel folders where your `.nc` files in your input directory. This file must be placed in the input directory. You can find it in `1.input/input4`.
$\hspace{1cm}$
- **`3.delete_output.py`** $\boldsymbol{\to}$ Interactively clears generated experiment results. When executed, this script provides custom prompts allowing you to selectively delete `img_output` folders (including any associated `Native` directories), `video_output` folders, or both. This enables you to preserve specific results while clearing unnecessary files.
$\hspace{1cm}$
- **`4.delete_requirements.py`** $\boldsymbol{\to}$ Completely uninstalls all requirements and model dependencies (***reclaiming ~10 GB of storage***) when you are finished working.
  
```bash
python 4.delete_requirements.py
```

> ***Note*** $\boldsymbol{\to}$ Don't worry about executing this file, this won't delete anything from your main python. Only **Python 3.10** will deleted alongside its **packages**.