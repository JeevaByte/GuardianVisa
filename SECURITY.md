# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| `main` branch | ✅ |

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

To report a security issue, use [GitHub's private vulnerability reporting](../../security/advisories/new) or email the maintainers directly.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive a response within **72 hours**. We will keep you updated throughout the process.

## Security Best Practices for Deployers

- **Never commit `.env` files** — use `.env.example` as a template
- **Never commit `service-account.json`** — use environment variables or Secret Manager
- Store all secrets in [Google Cloud Secret Manager](https://cloud.google.com/secret-manager) in production
- Rotate `GEMINI_API_KEY` and MongoDB credentials regularly
- Use MongoDB Atlas IP allowlisting in production

## Disclaimer

GuardianVisa is an **educational tool**, not a legal service. Do not store real student PII in production without proper data governance and legal review.
