# Helpdesk Ticket Data Fetch Tool

Công cụ Python dòng lệnh độc lập dùng để kết nối và kiểm tra dữ liệu `gerp.helpdesk.ticket` từ hệ thống Odoo/GERP phụ qua giao thức JSON-RPC.

## 📂 Cấu trúc thư mục

```
tools/
├── config.json      # File chứa thông số kết nối API (base_url, db, login, password,...)
├── fetch_data.py    # Script Python kết nối JSON-RPC và in dữ liệu ra màn hình
└── README.md        # Hướng dẫn sử dụng
```

## ⚙️ Cấu hình (`config.json`)

```json
{
  "base_url": "http://localhost:8069",
  "db": "gerp-eoffice-v17",
  "login": "admin",
  "password": "admin",
  "ticket_id": 1,
  "stage_id": 1,
  "limit": 20
}
```

## 🚀 Cách chạy

Mở Terminal / Command Prompt và thực thi:

```bash
cd d:\Doimoi\dcg_helpdesk_project\tools
python fetch_data.py
```

## 📊 Kết quả xuất ra

Script sẽ tự động:
1. Đăng nhập hệ thống qua JSON-RPC (`common/login`) và in ra `UID`.
2. Tải danh sách 20 Ticket gần nhất (`gerp.helpdesk.ticket`) kèm thông tin Partner, Stage, Priority.
3. Tải Tracking Log lịch sử thay đổi của vé có `ticket_id` chỉ định (`mail.tracking.value`).
4. Tải danh sách các Trạng thái (`gerp.helpdesk.stage`).
