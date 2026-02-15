from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gene_marker_explorer.services.gene_service import GeneService


def main(GENE_SYMBOL: str):
    print(f"{'=' * 60}")
    print(f"  GeneMarker Explorer")
    print(f"{'=' * 60}\n")

    with GeneService() as service:
        # Step 1: Fetch gene metadata from Ensembl
        print(f"🔍 Looking up gene: {GENE_SYMBOL}")
        gene_info = service.get_gene_info(GENE_SYMBOL)

        if not gene_info:
            print(f" Gene '{GENE_SYMBOL}' not found in Ensembl.")
            return

        # Display gene metadata
        print(f"\n Ensembl Gene Information:")
        print(f"   Ensembl ID:  {gene_info.ensembl_id}")
        print(f"   Symbol: {gene_info.symbol}")
        print(f"   Description:     {gene_info.description}")
        print(f"   Sequence Region Name:    chr{gene_info.chromosome}")
        print(f"   Strand Information:    {gene_info.strand}")

        # Step 2: Fetch tissue expression from HPA
        print(f"\n Fetching tissue expression data...")
        ensembl_id = gene_info.ensembl_id
        expression_data = service.get_tissue_expression(ensembl_id)

        if not expression_data:
            print(f" No tissue expression data found for {GENE_SYMBOL}.")
            return

        # Display results
        print(f"\n HPA Gene Information:")
        print(f"   Gene:  {expression_data.gene}")
        print(f"   Ensembl ID: {expression_data.ensembl_id}")
        print(f"   Description:     {expression_data.gene_description}")
        print(f"   Tissue Expression:    chr{expression_data.tissue_expression}")

    print(f"\n{'=' * 60}")
    print("  Done!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    GENE_SYMBOL = "EGFR"
    main(GENE_SYMBOL)