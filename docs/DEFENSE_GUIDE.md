# Demo and defense guide

For the full 5–8 minute Chinese speaking script, timed demo path, and expanded Q&A, see [DEFENSE_SCRIPT.md](DEFENSE_SCRIPT.md). The checklist below is a quick run sheet.

## Live walkthrough

1. Start the app locally and open the Dashboard.
2. Enter a website you own or have permission to analyze; confirm authorization.
3. Explain that collection is an ordinary public HTTP GET, with redirect revalidation, public-address checks, pinned DNS, timeout, redirect, and body-size limits.
4. Open a technology card and show its source and matched value. Explain that rule weights create an internal confidence level, not a statistical probability.
5. Show the architecture graph and state that it is an inference from co-observed signals, not knowledge of the site’s private deployment.
6. If an AI endpoint is available, configure it in Settings, review the displayed payload, confirm the send, and open the generated text report. Otherwise demonstrate previously saved AI output only as a historical result.
7. Compare two saved scans. Describe missing matches as “not observed now,” not proof of removal.
8. Export HTML or JSON; for PDF, use the browser print dialog.

## Offline test fixtures

The repository includes two controlled HTML pages under `demo-sites/`. Automated tests serve them over loopback and pass the requests through the IP-pinned transport using test-only resolver substitution. The production scanner itself continues to block loopback and private destinations.

## Common questions

- **Can the system know a hidden server framework?** No. It reports observable public evidence and its limits.
- **Does high confidence mean an 85% probability?** No. It is a project-internal sum of rule weights capped at 100.
- **Does AI verify a detection?** No. The rule engine owns detection; AI explains supplied evidence and uncertainty.
- **Why block local scan targets but allow a local AI endpoint?** The scan URL is untrusted user input and could expose internal services. A private AI endpoint is an explicit configuration choice, isolated from the scanner.
- **Where are API keys saved?** Backend process memory only, until restart; never in SQLite, browser storage, reports, or API responses.
- **Does a missing match mean a site removed the technology?** No. It means only that the current response did not expose matching evidence.
