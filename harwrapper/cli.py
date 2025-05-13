import click
import logging
import json
from pathlib import Path
from har2warc.har2warc import HarParser

@click.group()
def cli():
    """Convert HAR files to WARC.GZ format."""
    pass

@cli.command(name="file")
@click.argument("input_file", type=click.Path(exists=True, readable=True))
@click.argument("output_file", type=click.Path(writable=True))
@click.option("--creator-suffix", default="", help="Optional suffix for the 'creator' field in the WARC header, e.g. 'Zeitkapsel 2023'")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def convert_file(input_file, output_file, verbose, creator_suffix):
    """Convert a single HAR file into a WARC.GZ file."""

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    with open(input_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Failed to parse JSON: {e}")

    if "log" not in data:
        logging.info("'log' key not found – wrapping input as 'log'")
        data = {"log": data}

    if creator_suffix and "creator" in data["log"]:
        original_version = data["log"]["creator"].get("version", "")
        data["log"]["creator"]["version"] = f"{original_version} {creator_suffix}"
        logging.info(f"Updated 'creator' field to: {data['log']['creator']['version']}")

    try:
        with open(output_file, "wb") as out_fh:
            parser = HarParser(reader=data, writer=out_fh)
            parser.parse(out_filename=output_file)
    except Exception as e:
        raise click.ClickException(f"Conversion failed: {e}")

    click.echo("Conversion completed successfully.")

@cli.command(name="folder")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("output_dir", type=click.Path())
@click.option("--creator-suffix", default="", help="Optional suffix for the 'creator' field in the WARC header")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def convert_folder(input_dir, output_dir, creator_suffix, verbose):
    """Recursively convert all HAR files in a folder to WARC.GZ format."""

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    har_files = list(input_dir.rglob("*.har"))
    if not har_files:
        click.echo("No HAR files found.")
        return

    click.echo(f"Found {len(har_files)} HAR files. Starting conversion...")

    for har_file in har_files:
        output_file = output_dir / f"{har_file.stem}.warc.gz"

        try:
            with open(har_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "log" not in data:
                logging.info(f"{har_file}: 'log' key not found – wrapping input as 'log'")
                data = {"log": data}

            if creator_suffix and "creator" in data["log"]:
                original_version = data["log"]["creator"].get("version", "")
                data["log"]["creator"]["version"] = f"{original_version} {creator_suffix}"
                logging.info(f"{har_file}: updated 'creator' field to: {data['log']['creator']['version']}")

            with open(output_file, "wb") as out_fh:
                parser = HarParser(reader=data, writer=out_fh)
                parser.parse(out_filename=str(output_file))

            click.echo(f"{har_file} → {output_file.name}")

        except Exception as e:
            logging.warning(f"Failed to convert {har_file}: {e}")

    click.echo("All convertible files processed.")

if __name__ == "__main__":
    cli()

