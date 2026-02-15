"""
Ensembl REST API connector.
Provides functionality to retrieve structured gene level metadata
from the Ensembl REST API using a gene symbol. The connector
handles symbol to ID resolution and full metadata lookup.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
import requests

from .base import BaseConnector


@dataclass
class GeneMetadata:
    """Represents gene level metadata retrieved from the Ensembl REST API."""

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
    Connector for interacting with the Ensembl REST API.

    """

    SPECIES = "homo_sapiens"

    @property
    def base_url(self) -> str:
        # Base URL for all Ensembl REST API requests.
        return "https://rest.ensembl.org"

    def _build_url(self, identifier: str, **kwargs) -> str:
        """
        Constructs the appropriate API endpoint URL.
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
        Parse the JSON requests returned by the Ensembl API.
        """
        try:
            return response.json()
        except ValueError as e:
            # Handles malformed or non-JSON responses.
            raise ValueError(f"Failed to parse JSON response: {e}")

    def get_gene_metadata(self, symbol: str) -> GeneMetadata:
        """
        Retrieves full gene metadata for a given gene symbol.
        """
        # Convert gene symbol to Ensembl ID
        xrefs = self.fetch(symbol, endpoint="xrefs")

        # If no results are returned, the symbol is invalid.
        if not xrefs:
            raise ValueError(f"Gene symbol not found: {symbol}")

        # Attempts to locate the entry explicitly labelled as a gene.
        ensembl_id = None
        for entry in xrefs:
            if entry.get("type") == "gene":
                ensembl_id = entry.get("id")
                break

        # If no entry was explicitly marked as a gene, fall back to the first returned request.
        if not ensembl_id:
            # Fall back to first entry if no explicit gene type
            ensembl_id = xrefs[0].get("id")

        # If still unresolved, raise an error.
        if not ensembl_id:
            raise ValueError(f"Could not find Ensembl ID for: {symbol}")

        # Retrieve the full gene details using the Ensembl ID.
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