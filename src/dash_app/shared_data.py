"""Nguồn dữ liệu duy nhất cho mọi trang Dash.

Các trang CHỈ import ORDERS / RFM / FILTER_OPTIONS từ đây —
không đọc CSV, không chạy lại pipeline trong từng trang.
Dữ liệu đã làm sạch bởi scripts/clean_data.py.
"""

from src.shared import data_service

ORDERS = data_service.load_orders()
RFM = data_service.load_rfm()
FILTER_OPTIONS = data_service.get_filter_options(ORDERS, RFM)
