# Architecture

```text
Browser (127.0.0.1)
  ├─ Vue 3 / TypeScript UI
  └─ /api requests
       └─ FastAPI
            ├─ URL validation → DNS resolution → IP-pinned HTTP GET
            ├─ HTML/meta/resource parsing → JSON fingerprint engine
            ├─ SQLite: scan summaries, technologies, evidence, AI reports
            └─ optional OpenAI-compatible endpoint (explicit user configuration)
```

The production launcher binds Uvicorn to `127.0.0.1`; Vite proxies `/api` to the same local API during development. The app has no account or authentication layer and is designed for one user on their own machine.

## Scan data flow

1. The user attests that the target is authorized.
2. The scanner accepts HTTP(S) URLs without embedded credentials, resolves the host, rejects any non-global DNS answer, and connects to the selected checked IP while retaining the hostname for Host and TLS validation.
3. Redirects are followed manually, with the same validation and pinning repeated for each destination. Proxy environment variables are ignored. Request timeout is 10 seconds, redirect limit is five, and response body limit is 5 MiB.
4. Only status, title, selected response headers, bounded meta values, and script/style paths are persisted. The response HTML is transient and never stored.
5. Rules match source-specific evidence; duplicated evidence is counted once and the summed weight is capped at 100. Scores below 40 are low, 40–69 medium, and 70–100 high.

## AI data flow

The user configures an OpenAI-compatible Base URL, key, and model. Configuration is held in the FastAPI process only. Before an analysis request, the UI displays the exact minimized payload (URL without query/fragment, response status/title, and technology evidence) and asks the user to confirm. The backend does not follow provider redirects, caps the response at 256 KiB, validates the chat response shape, redacts an echoed key, and stores only the resulting analysis text/model. Vue interpolates the text; it is never interpreted as HTML.

A private/local AI endpoint is permitted only after the user explicitly configures it. That exception does not apply to website scanning.

## Limits and uncertainty

- Fingerprints can miss obfuscated, bundled, or server-only technologies. Absence means “not observed,” not “removed.”
- The architecture graph connects technologies observed in one response and is labeled as a hypothesis, not a verified internal deployment diagram.
- The local app has no authentication. Keep it bound to loopback and do not expose it on a shared network.
- The authorization checkbox records user attestation; it cannot prove site ownership.
