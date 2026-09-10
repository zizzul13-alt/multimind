"""Reflex presentation host for MultiMind."""

# Import the isolated proving page before the production App is constructed so
# Reflex registers the route without coupling canonical Design-DNA into the
# application/core boundary.
from multimind_reflex import canonical_page as _canonical_page  # noqa: F401
