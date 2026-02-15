import click
from scripts.script import main


@click.command()
@click.argument("gene_symbol", type=str)
def cli(gene_symbol: str):
    """
    GeneMarker Explorer CLI

    Example:
        genemarker EGFR
    """
    main(gene_symbol)


if __name__ == "__main__":
    cli()
