import os
import shutil

source_path = 'CompressJPEG.online_512x512-image (7).jpg'
destination_path = 'static/images/CompressJPEG.online_512x512-image (7).jpg'

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(destination_path), exist_ok=True)

# Move the file
shutil.move(source_path, destination_path)

print(f"Moved {source_path} to {destination_path}")
