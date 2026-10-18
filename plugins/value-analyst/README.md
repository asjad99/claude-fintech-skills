# value-analyst plugin

This folder is the plugin itself. Full documentation (installation,
the SWEBOK-based engineering workflow, fintech rules, the value-investing
analyst, guardrails, configuration and testing) is in the
[repository README](../../README.md).

Quick check after changes:

```bash
claude plugin validate --strict .
python3 -m unittest discover -s tests
```

Research and decision support only. Not personal financial advice.
