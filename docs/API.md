# API

All routes use the local FastAPI service under `/api`. Scan creation is synchronous. Errors return a short `detail` message; the API does not return full page HTML.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Local service health |
| `POST` | `/api/scans` | Scan `{ "url": "https://…", "authorized": true }` |
| `GET` | `/api/scans?limit=30` | Recent scan summaries (AI content omitted, count retained), limit 1–100 |
| `GET` | `/api/scans/{scan_id}` | Scan summary, evidence-backed technologies, saved AI reports |
| `GET` | `/api/scans/{scan_id}/evidence` | Evidence grouped by technology |
| `POST` | `/api/scans/compare` | Compare `{ "first_scan_id": 1, "second_scan_id": 2 }` |
| `GET` | `/api/ai/config` | Configuration status and non-secret endpoint/model metadata |
| `POST` | `/api/ai/config` | Set `{ "base_url": "…", "api_key": "…", "model": "…" }` in memory |
| `DELETE` | `/api/ai/config` | Clear in-memory AI configuration |
| `POST` | `/api/ai/test` | Test the configured chat endpoint |
| `POST` | `/api/ai/analyze` | Analyze `{ "scan_id": 1, "confirm_data_sent": true }` |
| `GET` | `/api/reports` | Recent saved AI reports |
| `GET` | `/api/reports/{report_id}` | One saved AI report with its scan |
| `GET` | `/api/reports/{scan_id}/export?format=html\|json` | Export one scan report; HTML is print-friendly |

AI request bodies never return the API key. The AI analysis endpoint requires explicit confirmation and sends only a minimized structured summary. Private AI Base URLs are accepted because the user explicitly configures them; scan URLs continue to reject private/reserved addresses.
