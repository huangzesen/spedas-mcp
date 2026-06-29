"""Vendored PDS PPI backend (formerly the ``xhelio-pds`` / ``pdsmcp`` package).

Absorbed into spedas_mcp (issue #107) so the repo is self-contained. Exposes the
PDS library surface (catalog / metadata / fetch / cache / config / label_parser)
that the spedas_mcp facade dispatches to for ``source_type="pds"``. The package's
former standalone MCP server/CLI is dropped — the spedas_mcp facade replaces it.
"""

__version__ = "0.3.0"

from spedas_mcp.backends.pds.config import configure

__all__ = ["configure", "__version__"]
