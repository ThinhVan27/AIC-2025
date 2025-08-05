import json
import os

def create_json(root_dir, save_path, video_paths, fps=30):
    all_frames = []
    for L_dir in sorted(os.listdir(root_dir), key=lambda x: int(x[1:])):
        for V_dir in sorted(os.listdir(os.path.join(root_dir, L_dir)), key=lambda x: int(x[1:])):
            frame_dir = os.path.join(root_dir, L_dir, V_dir)
            frames = sorted(os.listdir(frame_dir), key=lambda x: int(x[:-4].split('_')[1]))

            for frame in frames:
                if not frame.endswith('.jpg'):
                    continue

                frame_path = os.path.join(frame_dir, frame)
                L = int(L_dir[1:])
                V = int(V_dir[1:])
                frame_id = int(frame[:-4].split('_')[1]) 
                
                frame_metadata = {
                    "path": frame_path,
                    "video_path": video_paths[f"{L_dir}_{V_dir}"],
                    "L": L,
                    "V": V,
                    "frame_id": frame_id,
                    "fps": fps,
                    "frame_stamp": (frame_id//fps)+1,
                    "detected_objects": [],  # Placeholder for detected objects
                    "objects_count": {},  # Placeholder for objects count  
                    "detection": "",  # Placeholder for detection string
                    "text": []  # Placeholder for text data
                }

                # Append the frame data to the list
                all_frames.append(frame_metadata)

    # Save the collected frame data to a JSON file
    with open(save_path, 'w') as json_file:
        json.dump(all_frames, json_file, indent=4)
        print(f"Data saved to {save_path}")

if __name__ == "__main__":
    root_dir = 'data'
    save_path = 'metadata.json'
    video_paths = {
        "L15_V001": "L15\\V001.mp4",
        "L15_V002": "L15\\V002.mp4",
        "L16_V001": "L16\\V001.mp4",
        "L16_V002": "L16\\V002.mp4"
    }
    
    create_json(root_dir, save_path, video_paths)