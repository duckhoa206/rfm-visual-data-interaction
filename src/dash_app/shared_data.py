"""Dữ liệu dùng chung, nạp một lần khi khởi động dashboard."""

from src.shared import data_service

ORDERS = data_service.load_orders()
RFM = data_service.load_rfm()
FILTER_OPTIONS = data_service.get_filter_options(ORDERS, RFM)
WALMART = data_service.load_walmart()
BIGMART = data_service.load_bigmart()
