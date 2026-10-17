"""Money and number discipline for the value-analyst plugin.

Rules applied here (paraphrased from the Fintech Engineering Handbook,
"Representing Money" chapter):

* Never use binary floating point for money. Everything is decimal.Decimal,
  and values cross JSON boundaries as strings, never as bare JSON numbers.
* An amount is always paired with its currency. Arithmetic across different
  currencies is refused; conversion needs an explicit, directional FX rate
  that carries its source and date.
* Currencies come from a controlled set; unknown codes are rejected.
* Round rarely, explicitly, and only at boundaries (display / persistence).
  Splitting an amount tracks the residual instead of silently dropping it.
"""
from __future__ import annotations

import decimal
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation

CTX = decimal.Context(prec=34, rounding=ROUND_HALF_EVEN, traps=[
    decimal.InvalidOperation, decimal.DivisionByZero, decimal.Overflow])
decimal.setcontext(CTX)

# Controlled currency set: ISO 4217 code -> minor-unit digits.
# Deliberately not "2 for everything" (JPY has 0, KWD/BHD have 3).
CURRENCIES: dict[str, int] = {
    "USD": 2, "EUR": 2, "GBP": 2, "AUD": 2, "NZD": 2, "CAD": 2, "CHF": 2,
    "JPY": 0, "KRW": 0, "CNY": 2, "HKD": 2, "SGD": 2, "INR": 2, "SEK": 2,
    "NOK": 2, "DKK": 2, "ZAR": 2, "BRL": 2, "MXN": 2, "TWD": 2, "ILS": 2,
    "PLN": 2, "KWD": 3, "BHD": 3,
}

# Non-currency units a fact may carry.
UNITS = {"shares", "ratio", "pct", "count", "days", "years", "per_share"}


class MoneyError(ValueError):
    pass


def D(value) -> Decimal:
    """Parse to Decimal. Refuses floats so precision loss can't sneak in."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        raise MoneyError(f"float {value!r} refused: pass numbers as strings")
    if isinstance(value, bool):
        raise MoneyError("bool is not a number")
    try:
        s = str(value).strip().replace(",", "").replace("_", "")
        if s.startswith("(") and s.endswith(")"):  # accounting negatives
            s = "-" + s[1:-1]
        d = Decimal(s)
    except (InvalidOperation, TypeError) as exc:
        raise MoneyError(f"not a decimal number: {value!r}") from exc
    if not d.is_finite():
        raise MoneyError(f"non-finite number refused: {value!r}")
    return d


def check_currency(code: str) -> str:
    code = (code or "").upper()
    if code not in CURRENCIES:
        raise MoneyError(f"currency {code!r} is not in the controlled set")
    return code


def check_unit(unit: str) -> str:
    if unit in UNITS:
        return unit
    return check_currency(unit)


def is_currency(unit: str) -> bool:
    return (unit or "").upper() in CURRENCIES


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        object.__setattr__(self, "amount", D(self.amount))
        object.__setattr__(self, "currency", check_currency(self.currency))

    def _same(self, other: "Money"):
        if not isinstance(other, Money):
            raise MoneyError("can only combine Money with Money")
        if other.currency != self.currency:
            raise MoneyError(
                f"cross-currency arithmetic refused: {self.currency} vs "
                f"{other.currency}; convert explicitly with an FxRate first")

    def __add__(self, other):
        self._same(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        self._same(other)
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def times(self, factor) -> "Money":
        return Money(self.amount * D(factor), self.currency)

    def divided_by(self, divisor) -> "Money":
        return Money(self.amount / D(divisor), self.currency)

    def rounded(self, rounding=ROUND_HALF_EVEN) -> "Money":
        """Boundary rounding to the currency's ISO 4217 minor units."""
        q = Decimal(1).scaleb(-CURRENCIES[self.currency])
        return Money(self.amount.quantize(q, rounding=rounding), self.currency)

    def to_json(self) -> dict:
        return {"amount": str(self.amount), "currency": self.currency}

    def __str__(self):
        return f"{self.rounded().amount:,} {self.currency}"


@dataclass(frozen=True)
class FxRate:
    """Directional rate: 1 unit of base = rate units of quote.

    BASE/QUOTE is not the inverse of QUOTE/BASE in a real market (spread), so
    inversion is explicit and labelled. The source and date are part of the
    data because there is no canonical rate.
    """
    base: str
    quote: str
    rate: Decimal
    rate_date: str
    source: str
    kind: str = "reference"  # reference (valuation) | transactional

    def __post_init__(self):
        object.__setattr__(self, "base", check_currency(self.base))
        object.__setattr__(self, "quote", check_currency(self.quote))
        object.__setattr__(self, "rate", D(self.rate))
        if self.rate <= 0:
            raise MoneyError("FX rate must be positive")
        if not self.source or not self.rate_date:
            raise MoneyError("FX rate needs a source and a rate_date")

    def convert(self, money: Money) -> Money:
        if money.currency != self.base:
            raise MoneyError(
                f"rate is {self.base}/{self.quote}, amount is {money.currency}")
        return Money(money.amount * self.rate, self.quote)

    def inverted_reference(self) -> "FxRate":
        if self.kind != "reference":
            raise MoneyError("only reference (mid) rates may be inverted")
        return FxRate(self.quote, self.base, Decimal(1) / self.rate,
                      self.rate_date, self.source + " (inverted mid)")


def allocate(total: Money, weights: list) -> tuple[list[Money], Money]:
    """Split total by weights, rounding each part to minor units.

    Returns (parts, residual). Parts + residual == total exactly, so rounding
    never mints or loses money; the caller decides who owns the residual.
    """
    ws = [D(w) for w in weights]
    s = sum(ws)
    if s <= 0:
        raise MoneyError("weights must sum to a positive number")
    parts = [total.times(w / s).rounded(decimal.ROUND_DOWN) for w in ws]
    allocated = sum((p.amount for p in parts), Decimal(0))
    return parts, Money(total.amount - allocated, total.currency)


def round_display(value: Decimal, places: int = 2) -> str:
    q = Decimal(1).scaleb(-places)
    return f"{D(value).quantize(q, rounding=ROUND_HALF_EVEN):,}"
