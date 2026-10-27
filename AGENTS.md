# Project instructions

- Keep website scanning limited to ordinary GET requests for public HTTP(S) resources. Never add vulnerability probing, authentication bypass, or private-network scanning.
- Any URL that the scanner will fetch must be revalidated after redirects and connected through its validated public IP. Do not enable environment proxies for this path.
- AI Base URLs are user-selected and may target local/private services; never reuse that exception for scan targets. Keep API keys in backend memory only, redact them from generated output, and do not log or persist them.
- Do not persist page HTML. Store only bounded metadata and evidence required for explanations and history.
- Keep detected facts tied to evidence. Treat missing evidence as “not observed now”; label inferred architecture as a hypothesis.
- Use Vue text interpolation for AI and website content; do not render untrusted content with `v-html`.
- Add third-party source, version, license, and modification details to `THIRD_PARTY_NOTICES.md`. Check fingerprint data terms independently from source-code terms.
- Run backend tests and lint after backend changes; run frontend tests and production build after frontend changes. Report only commands actually run.
