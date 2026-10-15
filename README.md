# Phổ biến, tuyên truyền pháp luật về An ninh mạng

Webapp quiz tình huống vui về **Luật An ninh mạng số 116/2025/QH15** và **Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15**, cho học sinh, giáo viên và người dân. Trang tĩnh trên GitHub Pages (cùng cách làm với *Hôm nay ăn gì*), có thể bật thêm backend Supabase miễn phí.

- Người chơi: `index.html`. Nhập tên và tuổi, chơi 25 câu theo cấp (Cấp 1 ≤11 · Cấp 2 12–15 · Cấp 3 16–18 · Người lớn >18). Mỗi câu hiện số thứ tự “Câu x/25”, ảnh minh họa, đúng/sai, câu thần chú và căn cứ luật. Cuối phiên có thống kê. Lịch sử lưu trên thiết bị.
- Quản trị: `admin/`. Thêm, sửa, xóa câu hỏi; mỗi câu có mã số cố định. Có ảnh minh họa (URL hoặc tải lên), thống kê, Nhập/Xuất JSON và CSV, tài khoản quản trị.
- Ngân hàng câu hỏi: `questions.json`, sinh từ `bank/c1..c4.txt` bằng `python3 tools/build_bank.py`. Định dạng mỗi dòng: `cấp|độ khó|tags|ảnh|tình huống|đáp án đúng|sai1|sai2|sai3|câu thần chú|mã căn cứ`.
- Ảnh minh họa: `img/*.svg`, do nhóm tự vẽ, mỗi chủ đề một ảnh.

## Hai chế độ backend
1. **Không backend (mặc định)**: câu hỏi đọc từ `questions.json`. Trang quản trị đăng nhập bằng GitHub token (Contents: read/write trên repo này) và commit trực tiếp. Thống kê chỉ có trên từng thiết bị.
2. **Supabase (miễn phí)**: tài khoản Admin cao nhất có thể tạo quản trị viên khác. Thống kê toàn hệ thống được ghi phía server.
   1. Tạo project trên supabase.com rồi mở SQL Editor. Chạy `supabase/schema.sql`, sau đó chạy `supabase/seed.sql`.
   2. Chạy `select setup_super_admin('superadmin','<mật khẩu>');` đúng một lần (mật khẩu được lưu riêng, không có trong repo).
   3. Điền `SUPABASE_URL` và `SUPABASE_ANON_KEY` (anon/public key) vào `config.js`. Không bao giờ đưa `service_role` key vào repo.

Phần minh họa chỉ dùng để tuyên truyền, không thay thế văn bản luật. Điều, khoản trích dẫn được đối chiếu với văn bản đăng Công báo (congbao.chinhphu.vn).
