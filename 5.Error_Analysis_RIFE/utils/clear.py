import os
import shutil

def clear_folder(folder_path): 
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        
    os.makedirs(folder_path) 
    print(f"     -> {folder_path} successfully emptied!")

############################################################################################################################################################################

def clear_extenction(folder_path, extenction):
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if os.path.isfile(full_path) and filename.lower().endswith(extenction):
            try:
                os.remove(full_path)
                print(f"     -> Deleted: {filename}")
            except PermissionError:
                print(f"\n     -> Could not delete {filename} because it is currently in use by another program.")
            except Exception as e:
                print(f"\n     -> Failed to delete {filename}: {e}")