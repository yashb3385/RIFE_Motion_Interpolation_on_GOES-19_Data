import shutil
from pathlib import Path
print("\n")
channels_dir = "." 
path = Path(channels_dir)

for folder in path.iterdir():
    # To delete all Channel Folders (e.g., C01, C13)
    if folder.is_dir() and folder.name.startswith('C') and folder.name[1:].isdigit():
        print(f"Deleting directory: {folder}")
        shutil.rmtree(folder)

print("\nCleanup finished.\n")