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
        "idx": 0,
        "path": "keyframes/L21/V001/frame_000026.jpg",
        "video_url": "https://youtube.com/watch?v=Rzpw5WR7nAY",
        "L": "21",
        "V": "001",
        "frame_id": 26,
        "fps": 25,
        "frame_stamp": 1,
        "objects": "",
        "detection": "",
        "text": []
}
```
Ví dụ cho một frame cụ thể, ta có:
- **idx**: chỉ số tuyệt đối của frame trong toàn bộ dữ liệu.
- **path**: Đường dẫn tới file ảnh frame, tính từ thư mục gốc dữ liệu.
- **video_url**: URL của video.
- **L**: Số hiệu lớp (ví dụ: "15" tương ứng với L15)
- **V**: Số hiệu video trong lớp (ví dụ: "001" tương ứng với V001).
- **frame_id**: ID của frame trong video (bắt đầu từ 0).
- **fps**: Số frame trên giây của video gốc.
- **frame_stamp**: frame thuộc giây nào trong video.
- **objects**: Danh sách các object được phát hiện trong frame và số lượng, là `str`
- **detection**: Chuỗi mô tả kết quả nhận diện, là `str` (xem chi tiết ở `metadata.json`).
- **text**: Danh sách các đoạn text phát hiện trong frame (xem chi tiết ở `metadata.json`).

# Cập nhật 03/09/2025
## Cách tổ chức lại data tải từ phía BTC cung cấp

1. Tải và thiết lập cấu trúc thư mục như sau:
```
Root/
├── keyframes/
│   ├── L21_V001/
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
│   ├── L21_V002/
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
|   ├── ...
|      
├── map-keyframes/
│   ├── L21_V001.csv
│   ├── L21_V002.csv
|   ...
|
├── media-info/
│   ├── L21_V001.json
│   ├── L21_V002.json
|   ...
|
└── utils.py
```
2. Chạy trong termial (hiện đang ở `Root`) câu lệnh `python utils.py`. Sau khi chạy xong
- `keyframes` sẽ có cấu trúc `keyframes/Lxx/Vxxx/frame_id.jpg`
- Folder `metadata` tương ứng từng **L**