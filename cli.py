"""
Command line interface for GeneMarker Explorer.
Provides a simple wrapper around the main workflow,
allowing users to query a gene symbol directly from the terminal.
"""

import click
from scripts.script import main


@click.command()
@click.argument("gene_symbol", type=str)
def cli(gene_symbol: str):
    """
    Execute the gene lookup workflow for a given gene symbol.
    Example:
        genemarker EGFR
    """
    # Pass the provided gene symbol to the main workflow function
    main(gene_symbol)


if __name__ == "__main__":
    # Entry point for running the CLI directly
    cli()
