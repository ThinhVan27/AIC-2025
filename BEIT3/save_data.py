import json
from pymongo import MongoClient

uri = "mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

db = client['EEIoT_newbie']
collection = db['frames']

# collection.delete_many({})  # Clear the collection before inserting new data

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

collection.insert_many(data)

# collection.insert_one({
#     "path": "L15/V001/frame_000001.jpg",
#     "video_path": "L15/V001.mp4",
#     "L": 15,
#     "V": 1,
#     "frame": 124,
#     "fps": 30,
#     "frame_stamp": 4, # frame//fps
#     "detected_objects": ['car', 'pedestrian'],
#     "objects_count": {
#         "car": 1,
#         "pedestrian": 2
#     },
#     "detection": "e1car e2car d1car d3car c1pedestrian c2pedestrian f1pedestrian a1red a2blue a3green a4yellow a5yellow",
#     "text": ["Baber shop", "Car wash", "Grocery store"]
# })
