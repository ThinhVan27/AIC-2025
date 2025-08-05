# HƯỚNG DẪN FORMAT LƯU METADATA

Frame sau khi extract sẽ được lưu dưới dạng cây thư mục như sau:
```
Root/
├── L001/
│   ├── V001/
│   │   ├── frame_000001.jpg
│   │   ├── frame_000002.jpg
│   │   └── ...
│   ├── V002/
│   │   ├── frame_000001.jpg
│   │   ├── frame_000002.jpg
│   │   └── ...
|   ├── ...
|   |   
├── L002/
│   ├── V001/
│   │   ├── frame_000001.jpg
│   │   ├── frame_000002.jpg
│   │   └── ...
│   ├── V002/
│   │   ├── frame_000001.jpg
│   │   ├── frame_000002.jpg
│   │   └── ...
```

Mình sẽ lưu metadata của frame bằng file **JSON** với format như trong file `data.json` và `metadata.json`. Mọi người chuyển đổi kết quả từ mô hình và lưu theo định dạng đó. 
**Lưu ý**: Sau khi có các keyframe, mình sẽ khởi tạo file **JSON** mặc định như `metadata.json`, mọi người chỉ cần điền thêm vào trường cần thiết (detection, text), không cần khởi tạo lại.

```json
{
        "path": "data\\L15\\V001\\frame_0.jpg",
        "video_path": "L15\\V001.mp4",
        "L": 15,
        "V": 1,
        "frame_id": 0,
        "fps": 30,
        "frame_stamp": 1,
        "detected_objects": [],
        "objects_count": {},
        "detection": "",
        "text": []
}
```
Ví dụ cho một frame cụ thể, ta có:
- **path**: Đường dẫn tới file ảnh frame, tính từ thư mục gốc dữ liệu.
- **video_path**: Đường dẫn tới file video gốc chứa frame này.
- **L**: Số hiệu lớp (ví dụ: 15 tương ứng với L15).
- **V**: Số hiệu video trong lớp (ví dụ: 1 tương ứng với V001).
- **frame_id**: ID của frame trong video (bắt đầu từ 0).
- **fps**: Số frame trên giây của video gốc.
- **frame_stamp**: frame thuộc giây nào trong video.
- **detected_objects**: Danh sách các object được phát hiện trong frame, là `list[str]`
- **objects_count**: Thống kê số lượng từng loại object trong frame (ví dụ: `{"person": 2, "car": 1}`).
- **detection**: Chuỗi mô tả kết quả nhận diện (xem chi tiết ở `data.json`).
- **text**: Danh sách các đoạn text phát hiện trong frame (xem chi tiết ở `data.json`).
