import click
import logging
import json
from har2warc.har2warc import HarParser


@click.command()
@click.argument("input_file", type=click.Path(exists=True, readable=True))
@click.argument("output_file", type=click.Path(writable=True))
@click.option("--creator-suffix", default="", help="Optional addon for the 'creator'-field in the WARC-Header,f.e.'Zeitkapsel 2023'")
@click.option("--verbose", is_flag=True, help="Ausführliche Logausgabe aktivieren")
def main(input_file, output_file, verbose,creator_suffix):
    """
    Fixe fehlerhafte HAR-Dateien (falls nötig) und konvertiere sie mit har2warc.
Input_File .har-Datei, ggf. ohne log-Wrapper
Output_File .warc.gz-Datei, die geschrieben wird
    """

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    with open(input_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"Fehler beim Laden der JSON-Datei: {e}")

    if "log" not in data:
        logging.info("'log'-Key nicht gefunden – Eingabe wird als 'log'-Wert interpretiert")
        data = {"log": data}

    if creator_suffix and "log" in data and "creator" in data["log"]:
        original_version = data["log"]["creator"].get("version", "")
        data["log"]["creator"]["version"] = f"{original_version} {creator_suffix}"
        logging.info(f"'creator'-Feld angepasst: {data['log']['creator']['version']}")

    try:
        with open(output_file, "wb") as out_fh:
            parser = HarParser(reader=data, writer=out_fh)
            parser.parse(out_filename=output_file)
    except Exception as e:
        raise click.ClickException(f"Fehler bei der Verarbeitung: {e}")

    click.echo("Konvertierung erfolgreich abgeschlossen.")


if __name__ == "__main__":
    main()
