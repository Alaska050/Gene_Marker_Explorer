"""
Service layer for gene exploration.
Coordinates data retrieval from Ensembl (gene metadata)
and the Human Protein Atlas (tissue expression),
providing a unified interface for the CLI layer.
"""

from typing import Any, Dict, List, Optional

from connectors.ensembl import GeneMetadata
from connectors.hpa import HPAGeneData
from ..connectors.factory import ConnectorFactory


class GeneService:
    """
    Orchestrates the gene exploration workflow.
    """

    def __init__(self, timeout: int = 30):
        """
         Initialise the service with a configurable request timeout.
        """
        self.timeout = timeout
        self._ensembl = None
        self._hpa = None

    @property
    def ensembl(self):
        """Initialise the Ensembl connector when first accessed."""
        if self._ensembl is None:
            self._ensembl = ConnectorFactory.get_ensembl(timeout=self.timeout)
        return self._ensembl

    @property
    def hpa(self):
        """Initialise the HPA connector when first accessed."""
        if self._hpa is None:
            self._hpa = ConnectorFactory.get_hpa(timeout=self.timeout)
        return self._hpa

    def get_gene_info(self, gene_symbol: str) -> GeneMetadata:
        """
        Retrieve gene metadata from Ensembl.
        """
        return self.ensembl.get_gene_metadata(gene_symbol)

    def get_tissue_expression(
            self,
            ensembl_id: str
    ) -> HPAGeneData:
        """
        Retrieve tissue expression data from the Human Protein Atlas.
        """
        return self.hpa.get_tissue_expression(ensembl_id)

    def close(self) -> None:
        """
        Close any active connector sessions.
        """
        if self._ensembl:
            self._ensembl.close()
        if self._hpa:
            self._hpa.close()

    def __enter__(self):
        """Enable use as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connectors are closed when exiting context."""
        self.close()
        return False