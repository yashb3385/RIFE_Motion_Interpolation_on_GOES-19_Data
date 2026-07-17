import os
import shutil
import subprocess
import cv2
import numpy as np
from tqdm import tqdm  

def png_intermediate(png1_path, png2_path, png_inter_path):
    img1 = cv2.imread(png1_path, cv2.IMREAD_UNCHANGED)
    img2 = cv2.imread(png2_path, cv2.IMREAD_UNCHANGED)

    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    img1_16 = img1.astype(np.uint16)
    img2_16 = img2.astype(np.uint16)
    average_16 = (img1_16 + img2_16) // 2
    final_img = average_16.astype(np.uint8)
    cv2.imwrite(png_inter_path, final_img)

def video_to_img(video_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    ffmpeg_cmd = f'ffmpeg -y -i "{video_path}" -vsync 0 "{target_dir}/%04d.png"'
    ffmpeg_cmd += " -loglevel error" 
    subprocess.run(ffmpeg_cmd, shell=True)


def img_to_video(img_folder_path, output_video_path, fps):
    images = [img for img in os.listdir(img_folder_path) if img.endswith(".png")]
    images.sort()

    if not images:
        print("No images found in the target directory.")
    else:
        first_image_path = os.path.join(img_folder_path, images[0])
        first_frame = cv2.imread(first_image_path)
        height, width, layers = first_frame.shape

        output_dir = os.path.dirname(output_video_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        for img_name in tqdm(images, desc="Compiling Video Streams", unit="frame"):
            img_path = os.path.join(img_folder_path, img_name)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()
        cv2.destroyAllWindows()
        print(f"Success! Video stream compiled: {output_video_path}")

def merge_audio(video_sans_audio, audio_source, final_output):
    """
    Takes the audio track from audio_source and embeds it into video_sans_audio.
    """
    print("\n>>> Merging original audio track with interpolated video...")
    ffmpeg_cmd = (
        f'ffmpeg -y -i "{video_sans_audio}" -i "{audio_source}" '
        f'-c:v copy -c:a aac -map 0:v:0 -map 1:a:0? "{final_output}" -loglevel error'
    )
    subprocess.run(ffmpeg_cmd, shell=True)
    print(f"Success! Final audio-mapped video saved as: {final_output}")

if __name__ == "__main__":
    video_input = "input/15fps.mp4"
    processing_dir = "processing"
    original_dir = "processing/original"
    interpolated_dir = "processing/interpolated_image"
    
    temp_video_output = "output/temp_no_audio.mp4"
    final_video_output = "output/15fps_to_30fps.mp4"

    # --------------------------------------------------
    # Step 1: Extract frames from the original video
    # --------------------------------------------------
    print(">>> Step 1 : Extracting frames from video...")
    video_to_img(video_input, original_dir)

    # --------------------------------------------------
    # Step 2: Interleave original and intermediate frames 
    # --------------------------------------------------
    print("\n>>> Step 2 : Generating intermediate mathematical average frames...")
    os.makedirs(interpolated_dir, exist_ok=True)
    
    orig_files = [f for f in os.listdir(original_dir) if f.endswith(".png")]
    orig_files.sort()
    num_frames = len(orig_files)

    for i in tqdm(range(num_frames - 1), desc="Interpolating Frames", unit="pair"):
        img1_path = os.path.join(original_dir, orig_files[i])
        img2_path = os.path.join(original_dir, orig_files[i+1])

        orig_new_idx = (2 * i) + 1
        inter_idx = (2 * i) + 2

        orig_target_path = os.path.join(interpolated_dir, f"{orig_new_idx:04d}.png")
        inter_target_path = os.path.join(interpolated_dir, f"{inter_idx:04d}.png")

        shutil.copy2(img1_path, orig_target_path)
        png_intermediate(img1_path, img2_path, inter_target_path)

    if num_frames > 0:
        last_img_path = os.path.join(original_dir, orig_files[-1])
        last_new_idx = (2 * (num_frames - 1)) + 1
        last_target_path = os.path.join(interpolated_dir, f"{last_new_idx:04d}.png")
        shutil.copy2(last_img_path, last_target_path)

    # --------------------------------------------------
    # Step 3: Render processed frames into video & inject audio
    # --------------------------------------------------
    print("\n>>> Step 3 : Compiling sequential frame assets into video...")
    img_to_video(interpolated_dir, temp_video_output, 30)
    
    merge_audio(temp_video_output, video_input, final_video_output)
    
    if os.path.exists(temp_video_output):
        os.remove(temp_video_output)

    # --------------------------------------------------
    # Step 4: System folder sanitation cleanup
    # --------------------------------------------------
    print("\n>>> Step 4 : Deleting workspace directory environment setup...")
    if os.path.exists(processing_dir):
        shutil.rmtree(processing_dir)
        print("Processing environment successfully cleaned!")