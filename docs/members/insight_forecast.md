# Phân công RFM và Dự báo

**Phụ trách:** Phạm Quốc Duy

## Công việc

- Tính điểm RFM cho từng khách hàng.
- Chia khách hàng thành các nhóm để đề xuất cách chăm sóc.
- Xây dựng mô hình dự báo doanh thu theo tháng.
- Cung cấp biểu đồ và insight cho trang Dashboard.

## RFM

- **Recency:** khách hàng mua gần đây hay đã lâu chưa mua.
- **Frequency:** khách hàng mua bao nhiêu lần.
- **Monetary:** khách hàng đã chi bao nhiêu tiền.

Từ ba chỉ số trên, khách hàng được chia thành các nhóm như Champions, Loyal Customers, New Customers, Need Attention, At Risk và Lost.

## Dự báo

Mô hình dùng doanh thu theo tháng, xu hướng và mùa vụ. Dashboard cho phép xem khoảng 3 năm, 5 năm hoặc 10 năm với ba kịch bản:

- **Cơ sở:** tiếp tục theo xu hướng hiện tại.
- **Lạc quan:** doanh thu tăng tốt hơn.
- **Thận trọng:** doanh thu tăng chậm hoặc giảm.

MAE được hiển thị để người xem biết sai số tham khảo của mô hình. Kết quả dự báo dùng để hỗ trợ lập kế hoạch, không phải cam kết doanh thu chắc chắn.

## Tệp liên quan

- `src/shared/rfm_utils.py`: tính RFM.
- `src/shared/forecast_model.py`: tạo dự báo.
- `src/dash_app/pages/rfm.py`: trang RFM.
- `src/dash_app/pages/forecast.py`: trang Dự báo.
