import os
import sys
import random
import shutil

folder = sys.argv[1]

dst_folder = r"C:\Users\hidas.andras\Documents\SEM\Duna évszakos hiányzó\mixed_seasons"

for season in os.listdir(folder):
    container = []
    for root, dirs, files in os.walk(os.path.join(folder, season)):
        for file in files:
            if file.endswith(".tif") or file.endswith(".bmp"):
                container.append(os.path.join(root, file))
    if len(container) >= 100:
        selected_images = random.sample(container, 100)
    else:
        selected_images = container
    os.mkdir(os.path.join(dst_folder, season))
    for image_path in selected_images:
        shutil.copy(image_path, os.path.join(dst_folder, season))
