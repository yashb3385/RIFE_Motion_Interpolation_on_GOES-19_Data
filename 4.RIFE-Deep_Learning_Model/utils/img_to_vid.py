import os
import cv2

def png_to_video(img_folder_path, output_video_path, fps):
    images = [img for img in os.listdir(img_folder_path) if img.endswith(".png")]
    images.sort()

    if not images:
        print(f"\nNo images found in the directory {img_folder_path}.")
    else:
        first_image_path = os.path.join(img_folder_path, images[0])
        first_frame = cv2.imread(first_image_path)
        height, width, layers = first_frame.shape

        output_dir = os.path.dirname(output_video_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        print("\nWriting frames to video...")
        for img_name in images:
            img_path = os.path.join(img_folder_path, img_name)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()
        cv2.destroyAllWindows()
        print(f"     -> Success! Video saved as : {output_video_path}")