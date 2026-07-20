import os
from utils.clear import clear_folder

def clear_all_subfolders(base_dirs=["intermediate", "input"]):
    for base in base_dirs:
        print("")
        if os.path.exists(base):
            for item in os.listdir(base):
                item_path = os.path.join(base, item)
                # Check if it is a directory (like C01, C02, etc.)
                if os.path.isdir(item_path):
                    clear_folder(item_path)

clear_all_subfolders(["intermediate", "input"])
print("\n")