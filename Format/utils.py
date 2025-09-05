import json
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

def create_json(root_dir, save_dir, map_keyframes_dir, media_info_dir):
	idx = 0
	metadata = []
	pivots = []
 
	os.makedirs(save_dir, exist_ok=True)
	for i, V_dir in enumerate(sorted(os.listdir(os.path.join(root_dir)))):
		frame_url, fps, frame_ids, frame_stamps = "Not Found", 25.0, [], []

		# Get video url
		video_info_path = os.path.join(media_info_dir, f'{V_dir}.json')
		if os.path.exists(video_info_path):
			# Load video URL from the corresponding JSON file
			with open(video_info_path, 'r', encoding='utf-8') as f:
				video_info = json.load(f)
			video_url = video_info.get('watch_url', 'Not Found')

		# Get FPS, frame_id
		keyframe_info_path = os.path.join(map_keyframes_dir, f"{V_dir}.csv")
		if os.path.exists(keyframe_info_path):
			with open(keyframe_info_path, 'r') as f:
				reader = pd.read_csv(f)
				fps = reader['fps'].iloc[0]
				frame_ids = reader['frame_idx'].to_list()
				frame_stamps = reader['pts_time'].to_list()

		frame_dir = os.path.join(root_dir, V_dir)
		frames = sorted(os.listdir(frame_dir))

		L = V_dir[1:3]
		V = (V_dir[-3:])

		if V == "001":
			pivots.append(idx)
   
		for frame in frames:
			
			
			frame_id = frame_ids[int(frame[:-4])-1]
			frame_stamp = frame_stamps[int(frame[:-4])-1]

			frame_metadata = {
				"idx": idx,
				"path": f"keyframes/{V_dir[:3]}/{V_dir[-4:]}/frame_{str(frame_id).zfill(6)}.jpg",  # Normalize path for JSON
				"video_url": video_url,
				"L": L,
				"V": V,
				"frame_id": frame_id,
				"fps": fps,
				"frame_stamp": frame_stamp,
				"objects": "",
				"detection": "",  # Placeholder for detection string
				"text": []  # Placeholder for text data
			}
			idx += 1
			# Append the frame data to the list
			metadata.append(frame_metadata)
	
	# Extract metadata based on L and save to file
	pivots = pivots + [idx]
	for i in range(len(pivots)-1):
		pre = "L" if int(metadata[pivots[i]]['L'][:2])>=21 else "K"
		with open(os.path.join(save_dir, f"{pre}{metadata[pivots[i]]['L']}.json"), "w", encoding='utf-8') as f:
			json.dump(metadata[pivots[i]:pivots[i+1]], f, indent=4)
		
  
def process_file(old_path, new_path):
    """Move file từ old_path sang new_path"""
    shutil.move(old_path, new_path)

def rename(root, map_keyframes_dir, max_workers=8):
    for V_dir in os.listdir(root):
        V_path = os.path.join(root, V_dir)
        if os.path.isdir(V_path) and "_" in V_dir:
            # Tách Lxx và Vxxx
            L_part, V_part = V_dir.split("_")  # ví dụ: "L23", "V001"

            # Tạo thư mục đích mới
            new_dir = os.path.join(root, L_part, V_part)
            os.makedirs(new_dir, exist_ok=True)

            frame_ids = []
            keyframe_info_path = os.path.join(map_keyframes_dir, f"{V_dir}.csv")
            if os.path.exists(keyframe_info_path):
                reader = pd.read_csv(keyframe_info_path)
                frame_ids = reader['frame_idx'].to_list()

            # Danh sách task cho thread pool
            tasks = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for i, filename in enumerate(sorted(os.listdir(V_path))):
                    old_path = os.path.join(V_path, filename)
                    new_filename = f"frame_{str(frame_ids[i]).zfill(6)}.jpg"
                    new_path = os.path.join(new_dir, new_filename)

                    tasks.append(executor.submit(process_file, old_path, new_path))

                # Chờ tất cả task hoàn thành
                for future in as_completed(tasks):
                    future.result()  # nếu có lỗi sẽ raise ra ở đây

            # Xóa thư mục cũ sau khi move/copy xong
            os.rmdir(V_path)

if __name__ == "__main__":
    
	create_json(root_dir='keyframes',
			 save_dir='metadata',
			 map_keyframes_dir='map-keyframes',
			 media_info_dir='media-info'
			 )
 
	rename(root='keyframes',
        map_keyframes_dir='map-keyframes')