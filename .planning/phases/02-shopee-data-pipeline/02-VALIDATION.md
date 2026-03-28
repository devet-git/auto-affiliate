# Phase 2: Shopee Data Pipeline - Validation Strategy

## Nyquist Criteria

### Data Generation Rule
- Thử nghiệm việc cào danh sách sản phẩm mẫu theo từ khóa "áo thun nam" với max_item=10 để tiết kiệm thời gian, xác minh hàm crawler nhả ra kết quả chuẩn từ Shopee page.
- Test endpoint update Cookie storage state, verify JSON parse correctly.
- Test việc chạy thử Convert URL bằng mock/thủ thuật local nếu ko có real shoppe session, check log trace DB.

### Dimension 8 (Testing & Quality)
- Automated Unit tests cho model `ShopeeProduct`.
- Test function `scrape_keyword` bằng cách mock Playwright context hoặc dry-run headless pass. (Có thể test integration vào Phase 4 sau khi dựng xong các service Celery loop).
