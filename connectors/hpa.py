"""
Human Protein Atlas  connector.

Provides functionality to retrieve tissue level RNA expression
data for a given gene using the HPA JSON endpoint.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import requests

from .base import BaseConnector


@dataclass
class TissueExpression:
    """
     Represents RNA expression level for a specific tissue.
    """
    tissue: str
    ntpm: float


@dataclass
class HPAGeneData:
    """
    Represents structured gene expression data retrieved from HPA.
    """
    gene: str
    ensembl_id: str
    gene_description: str
    tissue_expression: List[TissueExpression]


class HPAConnector(BaseConnector):
    """
    Connector for the Human Protein Atlas API.
    Retrieves tissue level RNA expression data given a gene symbol
    or Ensembl ID.
    """
    @property
    def base_url(self) -> str:
        # Base URL for all HPA API requests.
        return "https://www.proteinatlas.org"

    def _build_url(self, identifier: str, **kwargs) -> str:
        """
        Construct the URL for querying HPA gene data.
        """
        return f"{self.base_url}/{identifier}.json"

    def _get_headers(self) -> Dict[str, str]:
        """Define request headers for HPA API calls."""
        return {
            "Accept": "application/json",
            "User-Agent": "GeneMarker-Explorer/0.1.0"
        }

    def _parse_response(self, response: requests.Response, **kwargs) -> Any:
        """
         Parse JSON response returned by the HPA API.
        """
        try:
            return response.json()

        # Handle invalid or malformed JSON responses
        except ValueError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")

    def _parse_tissue_expression(self, data: Dict[str, Any]) -> List[TissueExpression]:
        """
        Extract tissue level RNA expression data from raw HPA response.
        """
        expressions = []

        # HPA provides RNA expression data under the RNA tissue specific nTPM field.
        rna_tissues = data.get("RNA tissue specific nTPM", {})
        if isinstance(rna_tissues, dict):
            for tissue, ntpm in rna_tissues.items():
                try:
                    expressions.append(TissueExpression(
                        tissue=tissue,
                        ntpm=float(ntpm)
                    ))
                # Skip values that cannot be safely converted to float.
                except (ValueError, TypeError):
                    continue

        return expressions

    def get_tissue_expression(self, symbol: str) -> HPAGeneData:
        """
        Retrieve tissue RNA expression data for a given gene.
        """
        data = self.fetch(symbol)

        #  HPA may return either a list or a dictionary
        if isinstance(data, list):
            if not data:
                raise ValueError(f"No data found for gene: {symbol}")
            data = data[0]

        tissue_expression = self._parse_tissue_expression(data)

        # Map raw API fields into structured dataclass
        return HPAGeneData(
            gene=data.get("Gene"),
            ensembl_id=data.get("Ensembl"),
            gene_description=data.get("Gene description"),
            tissue_expression=tissue_expression
        )