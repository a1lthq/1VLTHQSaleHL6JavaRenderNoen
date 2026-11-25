# Highlands Coffee – Flask / Neon
Dùng database đã import, không chạy CREATE TABLE hoặc seed. Các truy vấn dùng public.mh, nhommh, kh, ddh, ctddh. Không sửa 12 bảng gốc. Đặt hàng khách vãng lai tạo KH mới và DDH + CTDDH trong một transaction, không trừ tồn kho, không thanh toán online. Không có đăng nhập, bình luận hoặc quản trị vì schema chưa có thông tin xác thực. Không lưu giá tại thời điểm mua vì CTDDH không có cột giá.

Copy ảnh gốc vào app/static/images (giữ nguyên tên file); nếu thiếu sẽ dùng placeholder. Không đưa file backup hay credentials lên GitHub.

Render: Python; root directory trống nếu repo chứa app và requirements.txt ngay gốc; build `pip install -r requirements.txt`; start `gunicorn app.index:app --bind 0.0.0.0:$PORT`; DATABASE_URL lấy từ Neon (postgresql://...), SECRET_KEY tạo ngẫu nhiên. Health check /health. Không cần Docker.

Local PowerShell: `py -m venv .venv`; `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`; đặt $env:DATABASE_URL và $env:SECRET_KEY; chạy `.\.venv\Scripts\python.exe -m flask --app app.index run`. Không sử dụng debug trên Internet.
