# Security Policy (SXJ / 事现鉴)

## Supported versions

The latest released version of the SXJ app and the current MAIP specification
are supported.

## Reporting a vulnerability

If you discover a security issue in SXJ (protocol, web app, Android app, or
mini-program), please report it privately:

- Email: **583272294@qq.com** with subject `SECURITY: <short description>`
- Do **not** open a public issue for active vulnerabilities.

We aim to acknowledge reports within 7 days and to propose a remediation
timeline. Credit will be given to reporters who wish to be named.

## Data handling

- SXJ is minimal-data by design (see PRIVACY.md); verification payloads are
  public facts, not personal data.
- No secret material is stored in client-side code; build secrets live only in
  CI configuration.
