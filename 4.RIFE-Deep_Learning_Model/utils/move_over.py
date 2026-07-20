import os
import shutil

def move(source_path, destination_folder):
    filename = os.path.basename(source_path)
    target_file_path = os.path.join(destination_folder, filename)

    if destination_folder:
        os.makedirs(destination_folder, exist_ok=True)

    if os.path.isfile(target_file_path):
        os.remove(target_file_path)
        print(f"->Existing file '{filename}' was overwritten.")
        
    shutil.move(source_path, destination_folder)