import requests
import os
import xml.etree.ElementTree as ET

def download_goes_file(year, day, hour, minute, channel, download_dir):
    day_str = f"{day:03d}"
    hr_str = f"{hour:02d}"
    min_str = f"{minute:02d}"
    ch_str = f"M6C{channel:02d}" # GOES-19 uses Mode 6
    
    # Construct the folder path
    prefix = f"ABI-L1b-RadF/{year}/{day_str}/{hr_str}/"
    url = f"https://noaa-goes19.s3.amazonaws.com/?list-type=2&prefix={prefix}"
    
    print(f"\nDEBUG : Checking {url}")
    
    response = requests.get(url)
    
    # If the response isn't successful, the folder might not exist
    if response.status_code != 200:
        print("   -> Error : Could not connect to AWS. Check your year/day/hour.")
        return

    root = ET.fromstring(response.content)
    files = root.findall('.//{http://s3.amazonaws.com/doc/2006-03-01/}Key')
    
    for f in files:
        os.makedirs(download_dir, exist_ok=True)
        filename = os.path.basename(f.text)
        # Pattern : sYYYYJJJHHMM (e.g., s20251401200)
        time_pattern = f"s{year}{day_str}{hr_str}{min_str}"
        
        # Check : Does filename have our channel AND our time pattern?
        if ch_str in filename and time_pattern in filename:
            print(f"   -> Found : {filename}")
            file_url = f"https://noaa-goes19.s3.amazonaws.com/{f.text}"
            
            with requests.get(file_url, stream=True) as r:
                r.raise_for_status()
                with open(os.path.join(download_dir, filename), "wb") as file:
                    for chunk in r.iter_content(chunk_size=8192):
                        file.write(chunk)
            print(f"   -> Successfully saved : {os.path.join('input', filename)}")

            return

    print("   -> Not Found : File not found for this specific time.")

download_folder = 'input'
download_goes_file(2024, 284, 19, 50, 13, download_folder)
print("\nDownload Finished!\n")