# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nhóm K3 Observability
- Repository URL: https://github.com/nguyen1oc/Day13-K3-Observability
- Commit SHA cuối: e8fe1d6dc646beff56cb6dba4e5cbea1ecbe8542
- Thành viên và vai trò:
  - Thành viên A (Logging & PII)
  - Thành viên B (Tracing & Prompt Versioning)
  - Thành viên C (Dashboard, SLO & Alerts)
  - Thành viên D (QA & Incident Analyst)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số traces: 10+ traces (Langfuse)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: config/dashboard.yaml (Validator: 6/6 panels hợp lệ)

## 3. Logging và tracing

- Evidence correlation ID: req-c5ba176d (Header x-request-id & log payload)
- Evidence PII redaction: Email, SĐT, CCCD, Credit Card đã được mã hóa/scrubbed
- Evidence trace waterfall: submission/evidence/trace_waterfall.png
- Giải thích một span đáng chú ý: Span `rag_retrieval` bị nghẽn (delay > 2.5s) do incident `rag_slow` gây ra.

## 4. Prompt versioning

- Prompt name: rag_prompt
- Version/label baseline: v1 (production)
- Version/label candidate: v2 (staging)
- Trace ID của mỗi version: submission/evidence/prompt_v1_trace.png, submission/evidence/prompt_v2_trace.png
- Bằng chứng đổi label hoặc rollback: submission/evidence/prompt_rollback.png

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ: 6/6 panel
- Evidence dashboard: submission/evidence/dashboard.png
- SLO đã chọn và lý do: Latency p95 < 2000ms & Error rate < 1%
- Alert rules và runbook: config/alert_rules.yaml & docs/alerts.md

## 6. Điều tra challenge

- Challenge ID: day13-k3-observability-v1 (Cohort: K3)
- Triệu chứng từ metrics: Latency xử lý API tăng đột biến từ ~150ms lên 15,030ms – 24,032ms (vượt ngưỡng SLA 2000ms) trên toàn bộ request tính năng `refund`.
- Trace ID liên quan: trace-challenge-refund-01
- Log line/correlation ID liên quan: req-1113cfc3, req-4dd348c8, req-1238972c, req-cf57f4b7, req-d0c8511c
- Root cause: Sự cố `rag_slow` được bật cho feature `refund`, gây ra nghẽn (sleep delay 2.5s mỗi retry) trong quá trình truy xuất Vector DB (`app/mock_rag.py`).
- Fix Action: Tắt cờ sự cố bằng API `POST /incidents/rag_slow/disable`.
- Preventive Measure: Đặt max timeout (1.5s) cho hàm `retrieve()` và thiết lập Alert rule khi RAG latency p95 > 2000ms trong 5 phút.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
