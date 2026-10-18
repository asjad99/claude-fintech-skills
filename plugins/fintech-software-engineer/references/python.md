# Python notes

Versions, packaging and tools come from the repo: `pyproject.toml`
(`requires-python`, `[tool.*]` sections), the lock file (`uv.lock`,
`poetry.lock`, `requirements*.txt`) and CI workflows. Use what the project
already uses; the names below are defaults for a new project.

## Commands (verify they match the repo's CI)
```
pytest
ruff check . && ruff format --check .
mypy --strict <package>        # or pyright, whichever the repo configures
pip-audit
```

## Money and dates
- `Decimal("12.34")` from strings or integers, never `Decimal(12.34)`.
- Quantize at boundaries with an explicit mode:
  `amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)`.
- `@dataclass(frozen=True) class Money: amount: Decimal; currency: str` with
  operators that reject mixed currencies.
- Pydantic or JSON output: serialise Decimal as a string.
- Timezone-aware datetimes (`zoneinfo`); `date` for value, settlement and due dates;
  inject the clock or use `time-machine` in tests.

## Code
- Type hints on every public function; the type checker runs in CI.
- Catch specific exceptions; a bare `except:` or `except Exception: pass` hides
  failures. Raise a domain error or return an explicit result.
- Validate inputs at boundaries (Pydantic models, or checks that raise
  `ValueError` with the offending value).
- Structured logging (`logging` with `extra=` or `structlog`).

## Tests
- pytest with test names that include the criterion id
  (`test_ac3_transfer_is_rejected_when_available_balance_is_too_low`).
- Hypothesis for property tests; `testcontainers` for database tests;
  approval or snapshot files for golden outputs.

## Tooling
The official `pyright-lsp` plugin gives Claude diagnostics and navigation.
