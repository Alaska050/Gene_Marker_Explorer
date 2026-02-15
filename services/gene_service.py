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

    def rank_tissues_by_expression(
            self,
            expression_data: List[Dict[str, Any]],
            top_n: Optional[int] = None,
            ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Rank tissues by nTPM expression level.
        """
        if not expression_data:
            return []

        # Sort by expression value
        sorted_data = sorted(
            expression_data,
            key=lambda x: x.get("nTPM", 0),
            reverse=not ascending
        )

        # Return top N entries if specified
        if top_n is not None and top_n > 0:
            return sorted_data[:top_n]

        return sorted_data

    def explore_gene(
            self,
            gene_symbol: str,
            top_n: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Run the complete gene exploration workflow:
        1. Fetch gene metadata from Ensembl
        2. Retrieve tissue expression from HPA
        3. Rank tissues by expression level
        """
        # Retrieve gene metadata.
        gene_info = self.get_gene_info(gene_symbol)

        if not gene_info:
            return None

        # Retrieve tissue expression using Ensembl ID.
        ensembl_id = gene_info.get("id")
        expression_data = self.get_tissue_expression(ensembl_id)

        # Rank tissues by expression level.
        ranked_tissues = self.rank_tissues_by_expression(
            expression_data or [],
            top_n=top_n
        )

        return {
            "gene_info": gene_info,
            "top_tissues": ranked_tissues,
            "total_tissues": len(expression_data) if expression_data else 0
        }

    def export_to_csv(
            self,
            expression_data: List[Dict[str, Any]],
            filepath: str,
            gene_symbol: Optional[str] = None
    ) -> None:
        """
        Export tissue expression data to CSV.

        Args:
            expression_data: List of tissue expression dictionaries.
            filepath: Path to output CSV file.
            gene_symbol: Optional gene symbol to include in output.
        """
        if not expression_data:
            raise ValueError("No expression data to export")

        fieldnames = ["rank", "tissue", "nTPM"]
        if gene_symbol:
            fieldnames.insert(0, "gene")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for rank, tissue_data in enumerate(expression_data, 1):
                row = {
                    "rank": rank,
                    "tissue": tissue_data.get("tissue", ""),
                    "nTPM": tissue_data.get("nTPM", 0)
                }
                if gene_symbol:
                    row["gene"] = gene_symbol

                writer.writerow(row)

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