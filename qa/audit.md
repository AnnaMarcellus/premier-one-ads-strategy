# Corrective webpage audit

## Verdict

- Earlier page: **FAIL**. It overstated verified research, supplied unsupported demand and bid ranges, described unverified advertisers and business capabilities, forecast revenue, and made operational timing claims. Its mobile navigation and print rules were not sufficient.
- Corrected page: **ready only for internal review**. This is not completed market research, a campaign forecast, or a launch-ready campaign. No publication, commit, push, Google Doc edit, account configuration, tracking installation, or ad spend occurred.

## Source boundary

Read the actual restored `index.html` and both supplied captures in full before editing.

- `C:/Users/Administrator/google_ads_kp_demolition_rows.json`: nine observed keyword rows, each with 10 average monthly searches. The other two rows are category headings. Exact keyword spelling, competition labels and displayed changes are preserved. Displayed dashes are explained as unavailable, not zero. No sourced bid or CPC estimate exists in these files.
- `C:/Users/Administrator/google_ads_kp_excavation_rows.json`: repeats the demolition results. It is not independent excavation evidence. Pagination text does not establish that a complete result set was captured or reviewed.
- Historical settings supplied from the prior transcript: Greenville County, South Carolina; English; Google; October 2025 through September 2026. The row files do not independently contain those settings. The page says this explicitly.
- Proposed 30-40 mile radius is separate from the historical county capture and requires approval of a business center, travel limits and exclusions. It is not an entire-county or DMA target.
- Official metric reference, verified by the parent research task and linked on the page: https://support.google.com/google-ads/answer/3022575. Average monthly searches include close variants and rounded counts. Competition describes relative advertisers, not buying intent. Historical top-of-page bids reflect the last 30 days and can be absent when historical bid information is limited. Missing bids do not prove zero spending. +infinity is not evidence of a surge by itself.
- The captures do not include column headers. The page labels the change columns according to the captured Planner layout and calls for a fresh export with headers before relying on trends.

## Corrective changes

- Replaced sales forecast framing with a research brief for Brian and the recommendation to validate before considering a capped test.
- Removed invented demand, keyword volume ranges, CPC and bid ranges, named competitor assertions, capability advantages, fleet and building-height claims, savings, revenues and ROI claims.
- Removed the private phone number and any embedded account identifiers. Preserved noindex while explaining that it does not secure a public URL.
- Retained demolition and excavation research categories as explicit pending checklists. No listed category is represented as confirmed service capability or completed research.
- Replaced the competitor section with pending advertiser validation and an evidence collection method.
- Described negative keywords as proposed and not installed. Flagged cheap and rental for contextual review rather than blanket blocking.
- Described missed-call handling and tracking as proposed, not implemented, with no promised response time.
- Calculator: arbitrary adjustable $12 illustrative CPC, requested 10%-15% scenario, $1,500 and $2,500 presets, unrounded intermediate values, two-decimal display and consistent CPL. No revenue, forced jobs, or budget-driven CPC reduction. It renders through the same function on load and after changes.
- Explained assumed full media deployment, uncertain auction volume, fee exclusions and that inquiries are not booked jobs. Included a fixed comparison table that remains available without JavaScript.
- All report data is visible without tabs or disclosures. Added labeled controls, keyboard focus, a skip link, wrapping navigation and scrollable data tables. Print uses dark text on white, repeated table headers and no hidden data sections.

## Real execution

Command: `python qa/test_page.py`

Final execution: 2026-11-06 03:48:47 UTC. Installed Python Playwright with **Chromium 151.0.7922.34**, loading the actual local file. **31 checks passed, 0 failed.** Machine-readable details: `qa/test-results.json`.

Measured checks include:

- Exact nine keyword rows, competition, displayed changes and unavailable bids match the demolition capture.
- Excavation capture repeats all nine demolition keywords.
- Legacy claim samples and private phone removed; noindex and official source link present.
- Calculator labels, initial rendering, both presets, unchanged CPC, fractional input precision, zero budget, both conversion rates at zero, one-sided zero conversion, invalid zero CPC, empty input and reversed conversion range.
- Keyboard Enter activates a budget preset with a visible focus style.
- No document or navigation overflow at **320, 375, 768 and 1440 CSS pixels**. Document scroll widths were exactly **320, 375, 768 and 1440** respectively. In-page service navigation worked at every width. Wide tables intentionally scroll within labeled regions.
- No tabs or disclosures remain, so hidden-panel interaction is not applicable.
- Browser reported **zero JavaScript errors**.
- Chromium printed a **7-page A4 PDF**. PyMuPDF extracted **10,444 text characters**, found every report heading, all nine keyword strings, both service lists and budget scenarios, and found no text outside PDF page bounds. Print styles rendered tested data text in dark colors.

The first PDF text assertion flagged wrapped keyword strings because it compared raw newlines. Inspection confirmed the strings were present across lines. The test now normalizes whitespace before checking; no missing content was excused. An initial evidence path inherited an unsuitable TMPDIR, so the final run explicitly writes evidence to the Hermes scratch directory.

## Visual inspection

Loaded actual desktop and mobile full-page screenshots through the vision tool, then inspected readable crops of the desktop opening, mobile navigation/hero and mobile calculator. Also inspected the rendered PDF first page. Dark amber identity is intact. Navigation wraps within the mobile viewport, text and labels remain readable, calculator controls stack, and no overlapping content was observed. The PDF has a white background, dark text and a readable table that continues with repeated headers. This is a focused visual and functional audit, not a WCAG certification or exhaustive cross-browser test.

## Evidence paths

All binary evidence is outside the repository under:
`C:/Users/Administrator/AppData/Local/hermes/cache/scratch/premier-one-corrective-audit/`

- `page-1440.png`: full-page desktop screenshot
- `page-768.png`: full-page tablet screenshot
- `page-375.png`: full-page mobile screenshot
- `page-320.png`: full-page narrow mobile screenshot
- `research-brief-print.pdf`: actual seven-page Chromium print
- `print-first-page.png`: rendered PDF first page for visual inspection
- `print-text.txt`: extracted PDF text

No screenshot or PDF assets were placed in the repository. Nothing was committed.

## Remaining blockers

1. Obtain a clean excavation export and complete the pending service-category research with visible settings and headers.
2. Validate actual advertisers with dated query and location evidence. No current advertiser participation is established.
3. Brian must approve services, licensing/insurance, capacity, offers, actual service radius and landing-page claims.
4. Implement and validate call/form tracking, routing and any compliant follow-up. None is installed by this page.
5. Approve an actual capped test plan, budget, duration, keyword settings, review cadence and pause criteria before spending.
6. This QA covers local Chromium only. No hosted deployment was performed or verified. Public noindex hosting is not confidential hosting.

## Files changed

- `C:/Users/Administrator/premier-one-ads-strategy/index.html`
- `C:/Users/Administrator/premier-one-ads-strategy/qa/test_page.py`
- `C:/Users/Administrator/premier-one-ads-strategy/qa/test-results.json`
- `C:/Users/Administrator/premier-one-ads-strategy/qa/audit.md`
