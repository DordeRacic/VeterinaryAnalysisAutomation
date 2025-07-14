import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
video_folder = base_dir / 'videos'
list_dir = base_dir
video_list = []

if video_folder.exists() and video_folder.is_dir():
    for video in video_folder.iterdir():
        if video.is_file():
            video_list.append(video.name)

else:
    print(f"Directory not found:{video_folder}")

output_path = base_dir / 'video_list.csv'
df = pd.DataFrame(video_list, columns=['Filename'])
df.to_csv(output_path, index=False)

print(f"Saved video filenames to {output_path}.")
