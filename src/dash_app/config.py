"""Cấu hình duy nhất cho sidebar Hub-and-Spoke.

Thêm / xóa / đổi tên / đổi thứ tự trang:
  1. Thêm file mới trong src/dash_app/pages/ (copy 1 file có sẵn).
  2. Sửa đúng bảng PAGE_META dưới đây (path, name, icon, order).
Sidebar tự sinh từ dash.page_registry nên không cần sửa code sidebar.
"""

PAGE_META = {
    "overview": {"path": "/", "name": "Tổng quan", "icon": "📊", "order": 0},
    "geo": {"path": "/geo", "name": "Phân tích địa lý", "icon": "🗺️", "order": 1},
    "rfm": {"path": "/rfm", "name": "Phân khúc RFM", "icon": "👥", "order": 2},
    "forecast": {"path": "/forecast", "name": "Dự báo", "icon": "📈", "order": 3},
}
