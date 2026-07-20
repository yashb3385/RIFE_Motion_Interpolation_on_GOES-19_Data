import os

def file_format_check(path, nc_folder_pattern):
    nc_entries = []
    png_files = []
    mp4_files = []

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if os.path.isfile(full_path):
            filename_lower = entry.lower()
            if filename_lower.endswith('.png'):
                png_files.append(entry)
            elif filename_lower.endswith('.mp4'):
                png_files.append(entry)

        elif os.path.isdir(full_path) and nc_folder_pattern.match(entry):
            nc_entries.append(entry)

    has_nc = len(nc_entries) > 0
    has_png = len(png_files) > 0
    has_mp4 = len(mp4_files) > 0

    existing_types_count = sum([has_nc, has_png, has_mp4])

    if existing_types_count > 1:
        print("\n" + "="*60)
        print(f"\n ERROR: Mixed file types detected in: '{path}'")
        print(f"   Strict Rule Broken: Only ONE type of file is allowed to exist.")
        print(f"   Current Detection status -> NC: {has_nc} | PNG: {has_png} | MP4: {has_mp4}")
        print("="*60 + "\n")
        return 
        
    elif existing_types_count == 0:
        print(f"\n WARNING: Folder '{path}' has no valid .nc, .png, or .mp4 files.")
        return 
    
    elif existing_types_count == 1:
        if has_nc:
            return nc_entries
        elif has_png:
            return png_files
        elif has_mp4:
            return mp4_files
        else: 
            pass