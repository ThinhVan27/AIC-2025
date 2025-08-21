import json
import os
from PIL import Image

def create_json(root_dir, save_path, video_paths, fps=30):
    idx = 0
    all_frames = []
    for L_dir in sorted(os.listdir(root_dir), key=lambda x: int(x[1:])):
        for V_dir in sorted(os.listdir(os.path.join(root_dir, L_dir)), key=lambda x: int(x[-3:])):
            frame_dir = os.path.join(root_dir, L_dir, V_dir)
            frames = sorted(os.listdir(frame_dir))

            for frame in frames:
                if not frame.endswith('.jpg'):
                    continue

                frame_path = os.path.join(frame_dir, frame)
                L = int(L_dir[-2:])
                V = int(V_dir[-3:])
                frame_id = int(frame[:-4]) 

                frame_metadata = {
                    "idx": idx,
                    "path": frame_path.replace('\\', '/'),  # Normalize path for JSON
                    "video_url": video_paths.get(f"{L_dir}_{V_dir}", "Not Found"),
                    "L": L,
                    "V": V,
                    "frame_id": frame_id,
                    "fps": fps,
                    "frame_stamp": (frame_id//fps)+1,
                    "objects": "",
                    "detection": "",  # Placeholder for detection string
                    "text": []  # Placeholder for text data
                }
                idx += 1
                # Append the frame data to the list
                all_frames.append(frame_metadata)

    # Save the collected frame data to a JSON file
    with open(save_path, 'w') as json_file:
        json.dump(all_frames, json_file, indent=4)
        print(f"Data saved to {save_path}")

def create_json_diff(root_dir, save_path, video_info_dir, fps=30):
    # Similar implementation as create_json but for diff structure data storage
    idx = 0
    all_frames = []
    for V_dir in sorted(os.listdir(root_dir)):
        L = int(V_dir[1:3])
        V = int(V_dir[-3:])
        frame_dir = os.path.join(root_dir, V_dir)
        frames = sorted(os.listdir(frame_dir))
        
        video_info_path = os.path.join(video_info_dir, f'{V_dir}.json')
        video_url = "Not Found"
        if os.path.exists(video_info_path):
            # Load video URL from the corresponding JSON file
            with open(video_info_path, 'r', encoding='utf-8') as f:
                video_info = json.load(f)
            video_url = video_info.get('watch_url', 'Not Found')
        
        for frame in frames:
            if not frame.endswith('.jpg'):
                continue

            frame_path = os.path.join(frame_dir, frame)
            frame_id = int(frame[:-4]) 

            frame_metadata = {
                "idx": idx,
                "path": frame_path.replace('\\', '/'),  # Normalize path for JSON
                "video_url": video_url,
                "L": L,
                "V": V,
                "frame_id": frame_id,
                "fps": fps,
                "frame_stamp": (frame_id//fps)+1,
                "objects": "car1 person1 person2 tree1 chair1 chair2",
                "detection": "a1car a2car d1person d2person c1person c2person g1tree g2tree a0chair a2chair",  # Placeholder for detection string
                "text": ["tạp", "hóa", "tuấn", "thoa", "xe", "máy", "nhà", "kính", "school"]  # Placeholder for text data
            }
            idx += 1
            # Append the frame data to the list
            all_frames.append(frame_metadata)

    # Save the collected frame data to a JSON file
    with open(save_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_frames, json_file, ensure_ascii=False, indent=4)
        print(f"Data saved to {save_path}")
              
if __name__ == "__main__":
    # root_dir = 'keyframes'
    # save_path = 'metadata.json'
    # video_info_dir = 'media-info'

    # # create_json_diff(root_dir, save_path, video_info_dir)
    # resize_image(root_dir)
    print(os.listdir())