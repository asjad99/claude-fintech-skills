#!/bin/bash
set -e
cat > allocate.py <<'PY'
def allocate(total, weights):
    """Split a cash dividend across holders in proportion to shares held."""
    s = sum(weights)
    return [round(total * w / s, 2) for w in weights]
PY
cat > test_allocate.py <<'PY'
from allocate import allocate


def test_two_equal_holders():
    assert allocate(100.00, [1, 1]) == [50.0, 50.0]
PY
