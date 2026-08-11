# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: high_latency_p95
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms <= 3000ms` (Target 99.5% requests qua cửa sổ 28 ngày)
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000ms` kéo dài liên tục trong `5m`
- Ảnh hưởng tới người dùng: Người dùng nhận phản hồi chậm, trải nghiệm giao tiếp với AI bị gián đoạn, thời gian chờ vượt mức chấp nhận được (> 3s).
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard kiểm tra panel **Latency percentiles** và **Request traffic** để xác định sự cố xảy ra do tải đột biến hay do thành phần xử lý nội bộ bị nghẽn.
  2. Mở Langfuse, lọc danh sách traces có `latency > 3000ms`, kiểm tra waterfall chart của trace để xác định span gây trễ (RAG retrieval `retrieve`, LLM generation `FakeLLM.generate`, hay middleware).
  3. Lấy `correlation_id` từ trace bất thường, tra cứu log trong `data/logs.jsonl` (tìm log `request_received` và `response_sent`) để kiểm tra payload, độ dài prompt, số lượng documents retrieve.
- Mitigation tạm thời:
  - Nếu do RAG retrieval chậm: bật cache cho retriever, giảm số lượng documents truy vấn (`doc_count`), hoặc chuyển sang chế độ fallback context ngắn.
  - Nếu do tải LLM: chuyển lưu lượng sang model dự phòng có độ trễ thấp hơn.
- Owner: ai-oncall

## Alert 2

- Tên: high_error_rate
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct <= 2.0%` (Target 99.0% requests qua cửa sổ 28 ngày)
- Điều kiện và thời gian duy trì: `error_rate_pct > 2.0%` kéo dài liên tục trong `5m`
- Ảnh hưởng tới người dùng: Người dùng nhận phản hồi lỗi HTTP 500 (`request_failed`), không nhận được câu trả lời từ AI service.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Error rate and breakdown** và endpoint `/metrics` để xem phân loại ngoại lệ trong `error_breakdown` (ví dụ: Timeout, RateLimitError, ConnectionError, InternalServerError).
  2. Mở Langfuse, lọc các trace có trạng thái `ERROR` để định vị chính xác vị trí phát sinh exception trong chuỗi call stack.
  3. Tra cứu file log `data/logs.jsonl` tìm các dòng có `event == "request_failed"` cùng `correlation_id` tương ứng để xem thông báo chi tiết trong `payload.detail`.
- Mitigation tạm thời:
  - Kích hoạt circuit breaker để tránh cascade failure.
  - Chuyển hướng traffic sang upstream LLM / cluster dự phòng.
  - Nếu lỗi do bad request / prompt format mới: rollback prompt version ngay lập tức.
- Owner: ai-oncall

## Alert 3

- Tên: low_quality_score
- Severity: warning
- SLI/SLO liên quan: `quality_score_avg >= 0.75` (Target 95.0% requests qua cửa sổ 28 ngày)
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75` kéo dài liên tục trong `10m`
- Ảnh hưởng tới người dùng: Chất lượng câu trả lời suy giảm, câu trả lời bị cụt, không liên quan đến ngữ cảnh hoặc bị redact quá mức khiến nội dung khó hiểu.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard panel **Quality proxy** để xác định thời điểm bắt đầu suy giảm chất lượng.
  2. Kiểm tra Langfuse xem gần đây có đợt cập nhật prompt (thay đổi `prompt_version`, chuyển label `candidate` sang `production`) hay không bằng cách xem metadata `prompt_version` và `prompt_label` trên traces.
  3. Kiểm tra log `response_sent` xem có sự xuất hiện bất thường của token `[REDACTED]` (do regex PII bắt nhầm từ khóa thông thường) hoặc `doc_count == 0` (RAG không tìm thấy tài liệu phù hợp).
- Mitigation tạm thời:
  - Rollback `prompt_label` về phiên bản stable trước đó trên Langfuse hoặc `.env`.
  - Tinh chỉnh lại bộ regex PII nếu phát hiện hiện tượng false positives khiến câu trả lời bị cắt xén.
- Owner: ai-oncall
