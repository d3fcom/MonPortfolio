import os
import shutil

def move_images():
    source_dir = 'images'
    destination_dir = 'static/images'
    
    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)
    
    # List of image files to move
    image_files = ['Screenshot 2024-10-01 052342.png', 'hoodstarclub.png', 'hoodstarshoes.png', 'wokies.png']
    
    for image in image_files:
        source_path = os.path.join(source_dir, image)
        destination_path = os.path.join(destination_dir, image)
        
        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
            print(f"Moved {image} to {destination_dir}")
        else:
            print(f"File {image} not found in {source_dir}")

if __name__ == "__main__":
    move_images()
