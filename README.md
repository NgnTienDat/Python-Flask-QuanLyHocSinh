# Python-Flask-QuanLyHocSinh

## Giới thiệu

Dự án **Python-Flask-QuanLyHocSinh** là một hệ thống quản lý học sinh được phát triển nhằm hỗ trợ các hoạt động quản lý học sinh trong trường học. Dự án được xây dựng bằng ngôn ngữ Python, sử dụng Flask Framework để xử lý backend và MySQL làm cơ sở dữ liệu. Frontend được xây dựng bằng HTML, CSS, tích hợp Bootstrap, và sử dụng template từ [ThemeWagon](https://themewagon.com/).

Dự án là đồ án môn **Công nghệ phần mềm** do giảng viên **Dương Hữu Thành** giảng dạy, thực hiện bởi 3 sinh viên:
- **Lê Quốc Trung**
- **Nguyễn Tiến Đạt**
- **Trần Quang Trường**

---

## Yêu cầu chức năng

### 1. Tiếp nhận học sinh
- Nhân viên của trường thực hiện tiếp nhận học sinh.
- Biểu mẫu tiếp nhận học sinh được thiết kế dễ sử dụng và trực quan.

### 2. Lập danh sách lớp
- Hệ thống tự động lập danh sách lớp cho học sinh.
- Nhân viên có thể điều chỉnh lớp của học sinh khi cần thiết.
- Biểu mẫu lập danh sách lớp hỗ trợ chỉnh sửa linh hoạt.

### 3. Nhập điểm và xuất điểm
- Giáo viên được phép nhập điểm từng môn học cho các học sinh trong một lớp.
- Biểu mẫu bảng điểm môn học giúp nhập liệu dễ dàng và chính xác.

### 4. Thống kê báo cáo
- Người quản trị có thể xem báo cáo tổng kết môn học theo từng lớp.
- Báo cáo được hiển thị với biểu đồ trực quan sử dụng **Chart.js**.

### 5. Thay đổi quy định
- Người quản trị được phép thay đổi các quy định sau:
  - Số tuổi tối đa và tối thiểu khi tiếp nhận học sinh.
  - Sĩ số tối đa của lớp học.
  - Quản lý môn học theo khối lớp (thêm, xóa, cập nhật, tìm kiếm).

---


## Công nghệ sử dụng

### Backend
- Python 
- Flask Framework
- MySQL

### Frontend
- HTML, CSS
- Bootstrap
- Template từ [ThemeWagon](https://themewagon.com/)
- Chart.js

---

## Cách chạy dự án

1. **Cài đặt môi trường**
   - Cài đặt Python.
   - Cài đặt MySQL.
   - Tạo môi trường ảo:
     ```bash
     python -m venv env
     ```
   - Cài đặt các thư viện cần thiết:
     ```bash
     pip install -r requirements.txt
     ```

2. **Cấu hình cơ sở dữ liệu**
   - Tạo cơ sở dữ liệu MySQL.
   - Cập nhật thông tin kết nối trong file `__init__.py`.
   - Chạy file `models.py` để tạo các bảng dữ liệu dưới database.

3. **Chạy ứng dụng**
   - Chạy ứng dụng Flask:
     ```bash
     python index.py
     ```
---


## Bản quyền

Dự án này thuộc bản quyền của nhóm phát triển: **Lê Quốc Trung**, **Nguyễn Tiến Đạt**, **Trần Quang Trường**.
