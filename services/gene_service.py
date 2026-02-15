import csv
from typing import Any, Dict, List, Optional

from connectors.ensembl import GeneMetadata
from connectors.hpa import HPAGeneData
from ..connectors.factory import ConnectorFactory


class GeneService:
    """
    Service layer that orchestrates the gene exploration pipeline.

    Coordinates between Ensembl (gene metadata) and HPA (tissue expression)
    to provide a unified interface for gene marker exploration.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the GeneService.

        Args:
            timeout: Request timeout for API calls in seconds.
        """
        self.timeout = timeout
        self._ensembl = None
        self._hpa = None

    @property
    def ensembl(self):
        """Lazy-load Ensembl connector."""
        if self._ensembl is None:
            self._ensembl = ConnectorFactory.get_ensembl(timeout=self.timeout)
        return self._ensembl

    @property
    def hpa(self):
        """Lazy-load HPA connector."""
        if self._hpa is None:
            self._hpa = ConnectorFactory.get_hpa(timeout=self.timeout)
        return self._hpa

    def get_gene_info(self, gene_symbol: str) -> GeneMetadata:
        """
        Fetch gene metadata from Ensembl.

        Args:
            gene_symbol: Human gene symbol (e.g., 'CD3D').

        Returns:
            Dictionary containing gene metadata or None if not found.
        """
        return self.ensembl.get_gene_metadata(gene_symbol)

    def get_tissue_expression(
            self,
            ensembl_id: str
    ) -> HPAGeneData:
        """
        Fetch tissue expression data from Human Protein Atlas.

        Args:
            ensembl_id: Ensembl gene ID (e.g., 'ENSG00000167286').

        Returns:
            List of tissue expression dictionaries or None if not found.
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

        Args:
            expression_data: List of tissue expression dictionaries.
            top_n: Number of top results to return (None for all).
            ascending: If True, sort lowest to highest.

        Returns:
            Sorted list of tissue expression dictionaries.
        """
        if not expression_data:
            return []

        # Sort by nTPM value
        sorted_data = sorted(
            expression_data,
            key=lambda x: x.get("nTPM", 0),
            reverse=not ascending
        )

        # Return top N if specified
        if top_n is not None and top_n > 0:
            return sorted_data[:top_n]

        return sorted_data

    def explore_gene(
            self,
            gene_symbol: str,
            top_n: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Complete gene exploration: fetch metadata and ranked expression.

        This is the main orchestration method that runs the full pipeline:
        1. Look up gene in Ensembl
        2. Fetch tissue expression from HPA
        3. Rank tissues by expression level

        Args:
            gene_symbol: Human gene symbol (e.g., 'CD3D').
            top_n: Number of top tissues to include.

        Returns:
            Dictionary with gene info and ranked tissue expression.
        """
        # Step 1: Get gene metadata
        gene_info = self.get_gene_info(gene_symbol)

        if not gene_info:
            return None

        # Step 2: Get tissue expression
        ensembl_id = gene_info.get("id")
        expression_data = self.get_tissue_expression(ensembl_id)

        # Step 3: Rank tissues
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
        """Close all connector sessions."""
        if self._ensembl:
            self._ensembl.close()
        if self._hpa:
            self._hpa.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False