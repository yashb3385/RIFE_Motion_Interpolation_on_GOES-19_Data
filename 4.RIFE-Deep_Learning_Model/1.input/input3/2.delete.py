import os

print("\n")

last_image_no = 326

i = 0
while i < (last_image_no + 1):

    path = f'{i:04d}.png'
    if os.path.exists(path):
        os.remove(path)
        print(f"Successfully removed path : {path}")
    i += 1

print("\nSuccessfully removed all images.\n")