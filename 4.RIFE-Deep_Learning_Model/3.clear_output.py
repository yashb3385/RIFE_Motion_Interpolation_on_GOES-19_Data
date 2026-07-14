import os
import shutil

print("\n")

def ask_y_n(ques):
    while True:
        ans = input(ques).strip().lower()
        if ans in ['y', 'n']:
            break 
        print("Invalid input! Please enter exactly 'y' or 'n'.")
    return ans

def clear_folder(folder_path): 
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        
    os.makedirs(folder_path) 
    print(f"  -> {folder_path} successfully emptied!")

parent_dir = "2.output"

if not os.path.exists(parent_dir):
    print(f"Error: Parent directory '{parent_dir}' could not be found.")
else:
    clear_img_choice = ask_y_n("Do you want to clear 'img_output' folders (and 'Native' folders)? [y/n] : ")
    clear_video_choice = ask_y_n("Do you want to clear 'video_output' folders? [y/n] : ")
    
    should_clear_img = (clear_img_choice == 'y')
    should_clear_video = (clear_video_choice == 'y')

    if not should_clear_img and not should_clear_video:
        print("\nOperation cancelled. No folders were modified.")
    else:
        print(f"\nScanning '{parent_dir}' for target folders...")
        cleared_img_count = 0
        cleared_video_count = 0
        cleared_native_count = 0 # New counter
        
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            
            if os.path.isdir(item_path) and item.startswith("output"):
                
                if should_clear_img:
                    target_img_folder = os.path.join(item_path, "img_output")
                    if os.path.exists(target_img_folder):
                        clear_folder(target_img_folder)
                        cleared_img_count += 1
                    
                    for sub_item in os.listdir(item_path):
                        if sub_item.startswith("Native"):
                            sub_item_path = os.path.join(item_path, sub_item)
                            if os.path.isdir(sub_item_path):
                                shutil.rmtree(sub_item_path)
                                cleared_native_count += 1
                                print(f"  -> Deleted Native folder: {sub_item_path}")

                if should_clear_video:
                    target_video_folder = os.path.join(item_path, "video_output")
                    if os.path.exists(target_video_folder):
                        clear_folder(target_video_folder)
                        cleared_video_count += 1
                        
        print("\n================================================")
        print("  Task Complete! Summary of cleared actions :")
        print("================================================")
        if should_clear_img:
            print(f"  -> Total 'img_output' folders cleared   : {cleared_img_count}")
            print(f"  -> Total 'Native' folders deleted       : {cleared_native_count}")
        if should_clear_video:
            print(f"  -> Total 'video_output' folders cleared : {cleared_video_count}")

print("\n")