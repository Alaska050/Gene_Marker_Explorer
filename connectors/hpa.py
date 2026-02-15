from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import requests

from .base import BaseConnector


@dataclass
class TissueExpression:
    """Data class representing tissue-level RNA expression."""

    tissue: str
    ntpm: float


@dataclass
class HPAGeneData:
    """Data class representing HPA gene expression data."""

    gene: str
    ensembl_id: str
    gene_description: str
    tissue_expression: List[TissueExpression]


class HPAConnector(BaseConnector):
    """
    Connector for the Human Protein Atlas API.

    Retrieves tissue-level RNA expression data given a gene symbol
    or Ensembl ID.
    """

    @property
    def base_url(self) -> str:
        return "https://www.proteinatlas.org"

    def _build_url(self, identifier: str, **kwargs) -> str:
        """
        Build URL for HPA gene lookup.

        Args:
            identifier: Gene symbol or Ensembl ID.

        Returns:
            Full URL for the HPA API endpoint.
        """
        return f"{self.base_url}/{identifier}.json"

    def _get_headers(self) -> Dict[str, str]:
        """Return headers for HPA requests."""
        return {
            "Accept": "application/json",
            "User-Agent": "GeneMarker-Explorer/0.1.0"
        }

    def _parse_response(self, response: requests.Response, **kwargs) -> Any:
        """
        Parse HPA API response.

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

    def _parse_tissue_expression(self, data: Dict[str, Any]) -> List[TissueExpression]:
        """
        Parse RNA tissue expression from HPA response.

        Args:
            data: Raw HPA gene data dictionary.

        Returns:
            List of TissueExpression objects.
        """
        expressions = []

        # HPA provides RNA expression in different formats
        # Try "RNA tissue specificity" data first
        rna_tissues = data.get("RNA tissue specific nTPM", {})
        if isinstance(rna_tissues, dict):
            for tissue, ntpm in rna_tissues.items():
                try:
                    expressions.append(TissueExpression(
                        tissue=tissue,
                        ntpm=float(ntpm)
                    ))
                except (ValueError, TypeError):
                    continue

        return expressions

    def get_tissue_expression(self, symbol: str) -> HPAGeneData:
        """
        Retrieve tissue RNA expression data for a gene.

        Args:
            symbol: Human gene symbol (e.g., "CD3D").

        Returns:
            HPAGeneData object with expression data.

        Raises:
            APIError: If the gene is not found.
            ParseError: If response parsing fails.
        """
        data = self.fetch(symbol)

        # HPA returns a list with one element or an object
        if isinstance(data, list):
            if not data:
                raise ValueError(f"No data found for gene: {symbol}")
            data = data[0]

        tissue_expression = self._parse_tissue_expression(data)

        return HPAGeneData(
            gene=data.get("Gene"),
            ensembl_id=data.get("Ensembl"),
            gene_description=data.get("Gene description"),
            tissue_expression=tissue_expression
        )