import click


def greet(name: str) -> str:
    """
    Simple test function that returns a greeting.
    """
    return f"Hello {name}"


@click.command()
@click.option(
    "--name",
    required=True,
    type=str,
    help="Your name."
)
def main(name: str):
    """
    Test CLI for GeneMarker Explorer.
    Prints a greeting message.
    """
    message = greet(name)
    click.echo(message)


if __name__ == "__main__":
    main()
