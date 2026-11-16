# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | | | |
| B | 50 | 5 | 60s | | | |
| C | 200 | 50 | 30s | | | |

1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.
2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.
3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.
4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.

| Scenario | Users | Spawn rate | Duration | p95 | Failures | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|
| A — Baseline | 10 | 2/s | 30s | 19 ms | 0/138 | 0% | 4.85 |
| B — Normal load | 50 | 5/s | 60s | 23 ms | 1/1,398 | 0.072% | 23.53 |
| C — Spike | 200 | 50/s | 30s | 51 ms | 5/2,859 | 0.175% | 97.99 |