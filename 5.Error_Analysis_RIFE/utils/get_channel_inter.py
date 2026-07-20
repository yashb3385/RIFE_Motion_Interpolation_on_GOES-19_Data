from pathlib import Path

def get_channel_inter_file(channel_no, base_dir="intermediate"):
    # Format channel string (e.g., '13' becomes 'C13')
    channel_dir = Path(base_dir) / f"C{int(channel_no):02d}"
    
    if not channel_dir.exists():
        print(f"Directory not found: {channel_dir}")
        return None, None

    real_files = tuple(p.name for p in channel_dir.glob("*.nc") if "inter" not in p.name)
    
    generated_files = tuple(p.name for p in channel_dir.glob("*.nc") if "inter" in p.name)
    
    # Extract string paths
    real_file = str(channel_dir / real_files[0]) if real_files else None
    generated_file = str(channel_dir / generated_files[0]) if generated_files else None
    
    return real_file, generated_file