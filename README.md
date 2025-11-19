# FindingPATH-2

Trình mô phỏng các thuật toán tìm đường (DFS, BFS, Dijkstra, A*) trên mạng đường khu vực Khương Đình – Hà Nội. Backend Flask cung cấp API, frontend Leaflet trực quan hóa bản đồ và animation từng bước duyệt.

## Cấu trúc thư mục

```
backend/
├── __init__.py
├── algorithms.py
├── app.py
├── graph_loader.py
└── khuong_dinh.graphml
frontend/
├── index.html
├── map.js
└── style.css
```

- `khuong_dinh.graphml` chứa mẫu đồ thị (có thể thay thế bằng dữ liệu xuất từ OSMnx).
- `graph_loader.py` đọc GraphML, chuẩn hóa trọng số cạnh (đường ngập/tắc).
- `algorithms.py` hiện thực 4 thuật toán và trả về cả đường đi + danh sách bước để visualization.
- `frontend/` là ứng dụng Leaflet cho phép chọn Start/Goal, chạy thuật toán và xem animation.

## Chạy backend

Yêu cầu Python 3.10+ và Flask.

```bash
pip install flask
export FLASK_APP=backend.app
flask run --host 0.0.0.0 --port 8000
```

Server cung cấp:

- `GET /graph` – dữ liệu nút/cạnh để frontend vẽ bản đồ.
- `GET /path/<algorithm>?start=<id>&goal=<id>` – đường đi + các bước. `<algorithm>` là `dfs`, `bfs`, `dijkstra`, `astar`.

> **Ghi chú:** Nếu bạn thay GraphML bằng dữ liệu thực tế từ OSMnx, chỉ cần đảm bảo các thuộc tính `length`, `flooded`, `blocked` tồn tại; trọng số sẽ được tính lại tự động.

## Chạy frontend

Serve thư mục `frontend/` bằng HTTP server bất kỳ (hoặc mở trực tiếp `index.html`). Khi backend chạy ở `http://localhost:8000`, frontend sẽ tải đồ thị và gọi API để hiển thị kết quả.

Ví dụ với Python:

```bash
cd frontend
python -m http.server 8080
```

Sau đó truy cập `http://localhost:8080` trong trình duyệt.

> Nếu frontend không thể kết nối backend, nó sẽ tự động hiển thị dữ liệu mẫu offline để bạn vẫn quan sát được giao diện.

## Cách sử dụng

1. Vào trang web, click 2 node bất kỳ để đặt `Start` và `Goal`.
2. Chọn một thuật toán (DFS, BFS, Dijkstra, A*). Backend trả về `path` và `steps`:

```json
{
  "path": ["1", "2", "5", "6"],
  "steps": [
    {"current": "1", "visited": ["1"], "frontier": ["4", "2"]},
    {"current": "2", "visited": ["1", "2"], "frontier": ["4", "5", "3"]}
  ]
}
```

3. Frontend dùng `steps` để highlight node đang xét (vàng), node đã duyệt (cam), frontier/open set (xanh lam). Đường kết quả cuối được tô xanh lá.
4. Dùng slider để chỉnh tốc độ animation (50–300 ms). Nút “Reset lựa chọn” để chọn lại Start/Goal.

## Kiểm thử

- Thử ít nhất 5 cặp điểm khác nhau trong đồ thị mẫu.
- Sử dụng các cạnh `flooded` và `blocked` (hiển thị xanh/đỏ) để xác nhận Dijkstra/A* ưu tiên đường có trọng số thấp hơn.

## Tùy biến thêm

- Có thể mở rộng backend để nhận thêm thuộc tính (ví dụ `speed`, `name`).
- Frontend có thể đọc GeoJSON/tiles thực tế nếu bạn xuất dữ liệu đầy đủ từ OSMnx.
