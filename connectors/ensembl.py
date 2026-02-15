from typing import Any, Dict, Optional
from dataclasses import dataclass
import requests

from .base import BaseConnector


@dataclass
class GeneMetadata:
    """Data class representing gene metadata from Ensembl."""

    ensembl_id: str
    symbol: str
    name: str
    description: str
    biotype: str
    chromosome: str
    start: int
    end: int
    strand: int
    species: str


class EnsemblConnector(BaseConnector):
    """
    Connector for the Ensembl REST API.

    Retrieves gene metadata given a human gene symbol using the
    /xrefs/symbol endpoint followed by /lookup for full details.
    """

    SPECIES = "homo_sapiens"

    @property
    def base_url(self) -> str:
        return "https://rest.ensembl.org"

    def _build_url(self, identifier: str, **kwargs) -> str:
        """
        Build URL for symbol lookup.

        Args:
            identifier: Gene symbol (e.g., "CD3D").

        Returns:
            Full URL for the xrefs/symbol endpoint.
        """
        endpoint = kwargs.get("endpoint", "xrefs")

        if endpoint == "xrefs":
            return f"{self.base_url}/xrefs/symbol/{self.SPECIES}/{identifier}"
        elif endpoint == "lookup":
            return f"{self.base_url}/lookup/id/{identifier}"
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

    def _parse_response(self, response: requests.Response, **kwargs) -> Any:
        """
        Parse Ensembl API response.

        Args:
            response: HTTP response object.

        Returns:
            Parsed JSON data.

        Raises:
            ParseError: If JSON parsing fails.
        """
        try:
            return response.json()
        except ValueError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")

    def get_gene_metadata(self, symbol: str) -> GeneMetadata:
        """
        Retrieve full gene metadata for a given symbol.

        This performs a two-step lookup:
        1. Convert symbol to Ensembl ID via /xrefs/symbol
        2. Get full details via /lookup/id

        Args:
            symbol: Human gene symbol (e.g., "CD3D").

        Returns:
            GeneMetadata object with full gene information.

        Raises:
            APIError: If the gene symbol is not found.
            ParseError: If response parsing fails.
        """
        # Step 1: Symbol to Ensembl ID
        xrefs = self.fetch(symbol, endpoint="xrefs")

        if not xrefs:
            raise ValueError(f"Gene symbol not found: {symbol}")

        # Find the gene entry (filter by type)
        ensembl_id = None
        for entry in xrefs:
            if entry.get("type") == "gene":
                ensembl_id = entry.get("id")
                break

        if not ensembl_id:
            # Fall back to first entry if no explicit gene type
            ensembl_id = xrefs[0].get("id")

        if not ensembl_id:
            raise ValueError(f"Could not find Ensembl ID for: {symbol}")

        # Step 2: Get full details
        details = self.fetch(ensembl_id, endpoint="lookup")

        return GeneMetadata(
            ensembl_id=details.get("id", ensembl_id),
            symbol=details.get("display_name", symbol),
            name=details.get("display_name", symbol),
            description=details.get("description", ""),
            biotype=details.get("biotype", "unknown"),
            chromosome=details.get("seq_region_name", ""),
            start=details.get("start", 0),
            end=details.get("end", 0),
            strand=details.get("strand", 0),
            species=details.get("species", self.SPECIES)
        )