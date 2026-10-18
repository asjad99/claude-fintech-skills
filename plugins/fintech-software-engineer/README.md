# fintech-software-engineer plugin

This folder is the plugin itself. Full documentation (installation, the
SWEBOK-based workflow, fintech rules, domain packs, guardrails and testing)
is in the [repository README](../../README.md).

Quick check after changes:

```bash
claude plugin validate --strict .
python3 -m unittest discover -s tests
```
