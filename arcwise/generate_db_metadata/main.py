import click

from .generate_db_metadata import run
from ..utils import coro


@click.command()
@click.option("--db-path", help="Path to input directory with sqlite dbs", required=True)
@click.option("--output-schemas-path", help="Path to output directory where schema SQL files will be saved", required=True)
@click.option("--tables-json", default="bird_evaluation/data/dev_tables.json", help="Path to input JSON file with table information")
@click.option("--output-metadata-file", default="bird_evaluation/data/dev_metadata.json", help="Filepath where output metadata JSON file will be saved")
@coro
async def main(db_path: str, output_schemas_path: str, tables_json: str, output_metadata_file: str) -> None:
    await run(db_path, output_schemas_path, tables_json, output_metadata_file)

if __name__ == "__main__":
    main()