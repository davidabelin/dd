"""Core Double-digits domain helpers.

This package owns the notebook-derived semantics that the rest of the repo
builds on top of: level tokens, curated and structured examples, image
composition helpers, dataset access, export layout, and notebook-lineage
compatibility wrappers.

The AIX-mounted and standalone runtimes both depend on these modules for the
canonical meaning of a Double-digits scene, so changes here affect the web app,
CLI, exported bundles, and model-training flows together.
"""

from dd_core.constants import ARITHMETIC_LEVEL, DOUBLE_LEVEL, SINGLE_LEVEL
from dd_core.examples import ExampleCatalog

__all__ = ["ARITHMETIC_LEVEL", "DOUBLE_LEVEL", "ExampleCatalog", "SINGLE_LEVEL"]
