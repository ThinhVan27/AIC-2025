Cách chạy:

```powershell
cd aic2026\search_engine
pip install -r requirements.txt
docker compose up -d
python search.py build --model all --recreate
```

Có thể tự chạy ở máy để build collection (phải tại embedding .npy về), hoặc tải ở [đây]() và đặt ở `search_engine/`
```powershell
python search.py build --model all --recreate
```

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