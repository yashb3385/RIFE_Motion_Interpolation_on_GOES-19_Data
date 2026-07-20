import requests
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def download_goes_files(start_dt, end_dt, channel, base_download_dir):

    base_url = "https://noaa-goes19.s3.amazonaws.com"
    channel_str = f"M6C{channel:02d}"
    
    # This will simply reuse the folder if it already exists
    target_dir = os.path.join(base_download_dir, f"C{channel:02d}")
    if (os.path.exists(target_dir) == 0):
        os.makedirs(target_dir)
    
    current_time = start_dt
    while current_time <= end_dt:
        year = current_time.strftime("%Y")
        doy = current_time.strftime("%j")
        hour = current_time.strftime("%H")
        
        prefix = f"ABI-L1b-RadF/{year}/{doy}/{hour}/"
        list_url = f"{base_url}?list-type=2&prefix={prefix}"
        
        print(f"\nChecking folder : {prefix}")
        
        try:
            response = requests.get(list_url)
            root = ET.fromstring(response.content)
            
            ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
            files = root.findall('s3:Contents', ns)
            
            found_any = False
            for f in files:
                key = f.find('s3:Key', ns).text
                filename = os.path.basename(key)
                
                if channel_str in filename and filename.endswith('.nc'):
                    # Extract start time from filename for comparison
                    try:
                        time_str = filename.split('_s')[1][:13] 
                        file_dt = datetime.strptime(time_str, "%Y%j%H%M%S")
                        
                        # Stop process if we pass the end time
                        if file_dt > end_dt:
                            print(f"\n[>] Completed Downloading Channel {channel} GOES-19 Data upto {end_dt}.\n")
                            return 
                        
                        if file_dt < start_dt:
                            continue
                    except (IndexError, ValueError):
                        pass

                    save_path = os.path.join(target_dir, filename)
                    
                    # Logic removed: no 'skip if exists' check. 
                    # It will now overwrite automatically.
                    print(f"\n  -> Downloading (Overwriting if exists) : {filename}")
                    file_url = f"{base_url}/{key}"
                    
                    with requests.get(file_url, stream=True) as r:
                        r.raise_for_status()
                        with open(save_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"     [Saved to: {save_path}]")
                    found_any = True
            
            if not found_any:
                print(f"  -> No valid files found in this hour.")
                
        except Exception as e:
            print(f"  -> Could not access or list folder: {e}")
            
        current_time += timedelta(hours=1)
    

channels = input("\nEnter the Channel Numbers separated by spaces to Download : ")
print("\n")
channels_list = [int(i) for i in channels.split()]

for i in channels_list:
    download_goes_files(
        start_dt=datetime(2025, 1, 1, 0, 0), # Year, Month, Day, Hour, Minute
        end_dt=datetime(2025, 1, 1, 0, 40), 
        channel=i, 
        base_download_dir="." 
    )

print("Process Completed.\n")
