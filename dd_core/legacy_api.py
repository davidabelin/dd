"""Notebook-lineage compatibility helpers.

This module preserves a small set of notebook-era helper names so older code
and notebook-derived references can continue to resolve without duplicating the
real implementations. New maintainer work should prefer the canonical modules
and classes in ``dd_core.examples``.
"""

from dd_core.examples import doubleDigits, getDoubleDigits, getOperator, get_results

__all__ = ["doubleDigits", "getDoubleDigits", "getOperator", "get_results"]
