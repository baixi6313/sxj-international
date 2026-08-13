# SXJ (事现鉴) — Digital Public Goods (DPG) Standard Assessment

> Prepared by the Light-Cone Operations Office (光锥运维部) · 2026-08-09
> Companion documents: `sxj-funding-request-en.html`, `SXJ-donor-institutions-en.md`
> Contact: **583272294@qq.com**

## Verdict — PASS (eligible for DPG nomination)

**SXJ meets the DPG Standard.** As of 2026-08-09, the compliance pack (`LICENSE` + 7 governance/docs) is pushed to **both** repositories:
- `baixi6313/sxj-2026-08-08` → **MIT**
- `baixi6313/sxj-android-app` → **Apache-2.0**

All 9 DPG indicators are now **green** (see nomination §F). The prior hard blocker (Indicator 2, no license) and the documentation/governance gaps (Indicators 3, 5, 7, 9A/B/C) are closed. SXJ qualifies as a DPG and can be nominated via digitalpublicgoods.net.

---

## 1. The 9 DPG Standard Indicators — mapped to SXJ

| # | Indicator | Requirement | SXJ status | Evidence / gap |
|---|-----------|-----------|------------|----------------|
| 1 | **SDG Relevance** | Relevant to one+ SDGs | ✅ PASS | SDG 1 (no poverty / social security), SDG 10 (reduced inequalities), SDG 16 (peace, justice, strong institutions), SDG 17 (partnerships). Rooted in UDHR Art. 22. |
| 2 | **Open Licensing** | OSI-approved open license on all code | ✅ **PASS** | MIT (`sxj-2026-08-08`) + Apache-2.0 (`sxj-android-app`), both at repo root. |
| 3 | **Clear Ownership** | Ownership of source clearly documented | ✅ PASS | `NOTICE` present in both repos (copyright + steward statement). |
| 4 | **Platform Independence** | Not locked to a proprietary platform | ✅ PASS | Web app + Android app + WeChat mini-program; core is an open spec (MAIP) implementable by anyone. No vendor lock-in. |
| 5 | **Documentation** | Readme / deploy / API docs | ✅ PASS | Root `README.md` + `CONTRIBUTING.md` now present in both repos. |
| 6 | **Non-PII Data Extraction** | Data extractable without PII | ✅ PASS | Verified public events (`events.html`, `evt_009/010`) concern system/link-availability; `PRIVACY.md` states non-PII policy. |
| 7 | **Privacy & Applicable Laws** | Complies with privacy law (GDPR etc.) | ✅ PASS | `PRIVACY.md` documents posture + GDPR alignment. |
| 8 | **Open Standards & Best Practices** | Uses open standards; documented APIs | ✅ PASS | MAIP is an open verification specification; light-cone coordinate model documented. |
| 9A | **Data Privacy & Security** | Secure handling of data | ✅ PASS | `SECURITY.md` present (vuln reporting + data handling). |
| 9B | **Inappropriate & Illegal Content** | Moderation policy | ✅ PASS | `GOVERNANCE.md` documents human-ratified content policy (MAIP R-1…R-6). |
| 9C | **Protection from Harassment** | Anti-harassment / CoC | ✅ PASS | `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1) present. |

**Summary:** 9 ✅ PASS — all indicators green.

---

## 2. SDG Relevance (Indicator 1) — detail

- **SDG 1 — No Poverty:** SXJ's ultimate aim is a verifiable global social-security layer (UDHR Art. 22), directly serving poverty resilience.
- **SDG 10 — Reduced Inequalities:** A neutral, jurisdiction-aware verification layer counters information asymmetry that disadvantages weaker parties.
- **SDG 16 — Peace, Justice & Strong Institutions:** Verifiable public facts strengthen institutional trust and accountability (anti-disinformation, public-interest verification).
- **SDG 17 — Partnerships:** Explicitly designed as a catalyst/spec that platforms and states adopt — not a centralised owner.

---

## 3. Nomination Readiness Checklist

- [x] Source code publicly available (GitHub: `baixi6313/sxj-2026-08-08`, `baixi6313/sxj-android-app`)
- [x] Platform-independent open protocol (MAIP) + multi-platform clients
- [x] Open data (public verification ledger `events.html`)
- [x] SDG relevance demonstrable
- [x] **OSI-approved license added** — MIT (primary) + Apache-2.0 (app)
- [x] Clear ownership / `NOTICE` statement
- [x] Root `README.md` + `CONTRIBUTING.md`
- [x] `PRIVACY.md` + `SECURITY.md` + `GOVERNANCE.md` + `CODE_OF_CONDUCT.md`

**Readiness: 100% — all 9 DPG indicators green. Ready to nominate.**

---

## 4. Remediation Plan (files to add before nomination)

| File | Purpose | Indicator |
|------|---------|-----------|
| `LICENSE` (MIT or Apache-2.0) | OSI-approved open license | 2 (blocker) |
| `NOTICE` | Copyright / ownership statement | 3 |
| `README.md` | What SXJ is, how to run, links | 5 |
| `CONTRIBUTING.md` | How to contribute | 5 |
| `PRIVACY.md` | Privacy posture, non-PII by design, GDPR alignment | 6, 7, 9A |
| `SECURITY.md` | Vulnerability reporting, data handling | 9A |
| `GOVERNANCE.md` | Ratifier (human arbitration) + MAIP R-1…R-6 + neutrality | 8, 9B |
| `CODE_OF_CONDUCT.md` | Anti-harassment | 9C |

**Recommended license:** **MIT** (permissive, OSI-approved, maximal adoption for a protocol/spec). Alternative: **Apache-2.0** (adds an explicit patent grant — advisable if SXJ's verification tooling is ever contested on patent grounds). Decision is the founder's; once chosen, the 8 files above are applied to both repos and the nomination can proceed.

---

## 5. Do-No-Harm by Design (already present, needs documentation)

SXJ's architecture embeds do-no-harm; it only needs to be *written down* to satisfy Indicators 6/7/9:

- **Human-ratified, not AI-decided:** MAIP R-1…R-6 retain all binding verdicts for humans; AI may suggest, never ratify.
- **Neutral catalyst, not owner:** Root→spec design means SXJ dissolves once adopted — no single interest can capture it.
- **Minimal data:** Verification payloads are public facts + density ρ, not personal profiles.
- **Jurisdiction-aware:** `j` axis respects each polity's own verification layer; no external hard标尺 imposed.

---

*This is an internal readiness assessment for the founder. It does not constitute a submitted nomination. Submit only after the §4 files are in place.*
