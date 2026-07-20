import os
from utils.ask import ask_y_n
from utils.clear import clear_folder

print("\n")

parent_dir = "2.output"

if not os.path.exists(parent_dir):
    print(f"Error : Parent directory '{parent_dir}' could not be found.")
else:
    clear_img_choice = ask_y_n("Do you want to clear 'img_output' folders (and 'Native' folders)? [y/n] : ")
    clear_video_choice = ask_y_n("Do you want to clear 'video_output' folders? [y/n] : ")
    clear_nc_choice = ask_y_n("Do you want to clear 'nc_output' folders? [y/n] : ")
    
    should_clear_img = (clear_img_choice == 'y')
    should_clear_video = (clear_video_choice == 'y')
    should_clear_nc = (clear_nc_choice == 'y')

    if not should_clear_img and not should_clear_video and not should_clear_nc:
        print("\nOperation cancelled. No folders were modified.")
    else:
        print(f"\nScanning '{parent_dir}' for target folders...")
        cleared_img_count = 0
        cleared_video_count = 0
        cleared_nc_count = 0
        
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            
            if os.path.isdir(item_path) and item.startswith("output"):
                
                if should_clear_img:
                    target_img_folder = os.path.join(item_path, "img_output")
                    if os.path.exists(target_img_folder):
                        clear_folder(target_img_folder)
                        cleared_img_count += 1

                if should_clear_video:
                    target_video_folder = os.path.join(item_path, "video_output")
                    if os.path.exists(target_video_folder):
                        clear_folder(target_video_folder)
                        cleared_video_count += 1
                
                if should_clear_nc:
                    target_nc_folder = os.path.join(item_path, "nc_output")
                    if os.path.exists(target_nc_folder):
                        clear_folder(target_nc_folder)
                        cleared_nc_count += 1
                        
        print("\n================================================")
        print("  Task Complete! Summary of cleared actions :")
        print("================================================")
        if should_clear_img:
            print(f"  -> Total 'img_output' folders cleared   : {cleared_img_count}")
        if should_clear_video:
            print(f"  -> Total 'video_output' folders cleared : {cleared_video_count}")
        if should_clear_nc:
            print(f"  -> Total 'nc_output' folders cleared : {cleared_nc_count}")

print("\n")