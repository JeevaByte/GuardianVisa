# Contributing to GuardianVisa

Thank you for helping protect international students! 🛡️

## How to Contribute

### Reporting Bugs
Open a [Bug Report issue](../../issues/new?template=bug_report.md) with:
- Steps to reproduce
- Expected vs actual behaviour
- Environment (OS, Python/Node version)

### Suggesting Features
Open a [Feature Request issue](../../issues/new?template=feature_request.md) describing:
- The problem it solves
- Who benefits (which visa type / scenario)
- Any proposed solution

### Submitting a Pull Request

1. **Fork** the repo and create a branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Set up locally** — follow the [Quick Start in the README](README.md#-quick-start-local)
3. **Make your changes** — keep commits focused and descriptive
4. **Test your changes**:
   ```bash
   make test          # runs backend + frontend tests
   ```
5. **Open a PR** against `main` — fill in the PR template

### Code Style
- **Python:** [Black](https://black.readthedocs.io/) formatter, PEP 8
- **JavaScript:** ESLint + Prettier (config in `frontend/`)
- Keep functions small and well-named; add docstrings to agent tools

### Areas We Welcome Contributions

| Area | Examples |
|------|---------|
| 🛂 Visa rules | Add/correct visa type rulesets in `data/` |
| 🔍 Scam patterns | Submit new scam pattern examples |
| 🌍 Internationalisation | Add support for non-US visa types (UK, Canada, Australia) |
| 🧪 Tests | Expand agent tool unit tests |
| 📚 Docs | Improve setup guides, add diagrams |
| ♿ Accessibility | UI improvements for screen readers |

## Code of Conduct

By participating, you agree to our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
