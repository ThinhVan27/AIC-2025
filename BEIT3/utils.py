import json
import os
import cv2
from PIL import Image

def create_json(root_dir, save_root, video_info_dir, fps=25):
    idx = 0
    for L_dir in sorted(os.listdir(root_dir)):
        metadata = []
        for V_dir in sorted(os.listdir(os.path.join(root_dir, L_dir))):
            frame_dir = os.path.join(root_dir, L_dir, V_dir)
            frames = sorted(os.listdir(frame_dir))
            for frame in frames:
                if not frame.endswith('.jpg'):
                    continue

                frame_path = os.path.join(frame_dir, frame)
                L = (L_dir[1:])
                V = (V_dir[1:])
                frame_id = int(frame[6:-4]) 

                video_info_path = os.path.join(video_info_dir, f'{L_dir[:3]}_{V_dir}.json')
                video_url = "Not Found"
                if os.path.exists(video_info_path):
                    # Load video URL from the corresponding JSON file
                    with open(video_info_path, 'r', encoding='utf-8') as f:
                        video_info = json.load(f)
                    video_url = video_info.get('watch_url', 'Not Found')

                frame_metadata = {
                    "idx": idx,
                    "path": frame_path.replace('\\', '/')[23:],  # Normalize path for JSON
                    "video_url": video_url,
                    "L": L,
                    "V": V,
                    "frame_id": frame_id,
                    "fps": fps,
                    "frame_stamp": (frame_id//fps),
                    "objects": "",
                    "detection": "",  # Placeholder for detection string
                    "text": []  # Placeholder for text data
                }
                idx += 1
                # Append the frame data to the list
                metadata.append(frame_metadata)

        # Save the collected frame data to a JSON file
        with open(os.path.join(save_root, f"{L_dir}.json"), 'w') as json_file:
            json.dump(metadata, json_file, indent=4)
            print(f"Data saved to {L_dir}")

if __name__ == "__main__":
    root_dir = 'drive/MyDrive/AIC-2025/keyframes'
    save_root = 'metadata'
    video_info_dir = 'media-info'
    os.makedirs(name=save_root, exist_ok=True)
    create_json(root_dir, save_root, video_info_dir)
