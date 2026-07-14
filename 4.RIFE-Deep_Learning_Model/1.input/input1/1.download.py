import subprocess
import zipfile
import os

git_file_path = "yashb3385/Data_Samples/main/tables_in_goes19_C13_data_format/C13.zip"
zip_file = os.path.basename(git_file_path)
destination = '.'

print("\n")
subprocess.run(f"curl -L -O https://raw.githubusercontent.com/{git_file_path}", shell=True)

def extract_zip(file_path, extract_to_dir):
    print("\n")
    if not os.path.exists(extract_to_dir):
        os.makedirs(extract_to_dir)
        print(f"Created directory: {extract_to_dir}")

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
            print(f"Successfully extracted '{file_path}' to '{extract_to_dir}'")
    except zipfile.BadZipFile:
        print(f"Error : '{file_path}' is not a valid zip file.")
    except FileNotFoundError:
        print(f"Error : The file '{file_path}' was not found.")
    print("\n")
    os.remove(file_path)

extract_zip(zip_file, destination)