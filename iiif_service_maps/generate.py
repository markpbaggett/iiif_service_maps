from csv import DictReader
import click
from iiif_service_maps import ManifestGenerator
from tqdm import tqdm


@click.group()
def cli() -> None:
    pass


@cli.command("generate", help="Generate manifest files from CSV.")
@click.option(
    "--csv",
    "-c",
    help="Base CSV File",
    required=True,
)
def generate_csv(csv: str) -> None:
    with open(csv, 'r') as input_csv:
        csv_reader = DictReader(input_csv)
        for row in tqdm(csv_reader):
            x = ManifestGenerator(row)
            x.write("output")


