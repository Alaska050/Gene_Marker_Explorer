"""
GeneMarker Explorer CLI

This script retrieves gene metadata from Ensembl and tissue expression data
from the Human Protein Atlas and provides simple CLI for querying gene level information.

"""


from __future__ import annotations

import sys # Used here to adjust Python's import path
from pathlib import Path # Making handling file paths cleaner

#Adding the project’s root directory to the Python path allowing the script to locate the gene_marker_explorer package when running directly from the terminal.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports the main service layer which coordinates API calls and handles the  gene lookup workflow.
from gene_marker_explorer.services.gene_service import GeneService


def main(GENE_SYMBOL: str):
    """
    Execute the gene lookup workflow for a given gene symbol.

    """

    # Displaying a CLI header for clarity.
    print(f"{'=' * 60}")
    print(f"  GeneMarker Explorer")
    print(f"{'=' * 60}\n")

    # Using GeneService as a context manager so that any sessions are properly opened and closed automatically.
    with GeneService() as service:
        # Retrieves core gene metadata from Ensembl.
        print(f"🔍 Looking up gene: {GENE_SYMBOL}")
        gene_info = service.get_gene_info(GENE_SYMBOL)

        # If no data returned from Ensembl for the gene, stops the program.
        if not gene_info:
            print(f" Gene '{GENE_SYMBOL}' not found in Ensembl.")
            return

        # Displays key information about the gene.
        print(f"\n Ensembl Gene Information:")
        print(f"   Ensembl ID:  {gene_info.ensembl_id}")
        print(f"   Symbol: {gene_info.symbol}")
        print(f"   Description:     {gene_info.description}")
        print(f"   Sequence Region Name:    chr{gene_info.chromosome}")
        print(f"   Strand Information:    {gene_info.strand}")

        # Use the Ensembl ID to query tissue expression data from the Human Protein Atlas.
        print(f"\n Fetching tissue expression data...")
        ensembl_id = gene_info.ensembl_id
        expression_data = service.get_tissue_expression(ensembl_id)

        # It handles the cases where expression data is unavailable.
        if not expression_data:
            print(f" No tissue expression data found for {GENE_SYMBOL}.")
            return

        # Displays the expression related metadata retrieved from HPA.
        print(f"\n HPA Gene Information:")
        print(f"   Gene:  {expression_data.gene}")
        print(f"   Ensembl ID: {expression_data.ensembl_id}")
        print(f"   Description:     {expression_data.gene_description}")
        print(f"   Tissue Expression:    {expression_data.tissue_expression}")

    # Closing banner to indicate completion.
    print(f"\n{'=' * 60}")
    print("  Done!")
    print(f"{'=' * 60}")

"""
Script entry point, prevents automatic execution if this file imported as a module.
"""
if __name__ == "__main__":
    GENE_SYMBOL = "EGFR" # Default gene used for testing.
    main(GENE_SYMBOL)