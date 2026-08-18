Vào `README.md` trong `model/` để kiểm tra và cài đặt checkpoint trước. 

Cách chạy:

```powershell
cd aic2026\search_engine
pip install -r requirements.txt
docker compose up -d
```

Có thể tự chạy ở máy để build collection bằng lệnh ở dưới (phải tại embedding .npy và metadata về)
```powershell
python search.py build --model all --recreate
```
hoặc tải ở [đây](https://drive.google.com/file/d/1mZGQNQ0bWFDxIw--3Ye_WgRan_TSOEt2/view?usp=sharing) và đặt ở `search_engine/`

Search text/image:

```powershell
python search.py text "a man riding a motorbike" --model beit3 --top-k 10
python search.py image "sample.jpg" --model beit3 --top-k 10
```

Dùng trong code:

```python
from aic2026.search_engine import text_search, image_search

results = text_search("a person walking on the street", model="beit3", top_k=20)
results = image_search("query.jpg", model="beit3", top_k=20)
```

# Lưu ý:
- Máy chạy beit3 cần `pip install transformers==4.57.1`, không thì `pip install transformers==5.15.0`