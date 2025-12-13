from argparse import ArgumentParser
from src.spreadsheet import Spreadsheet


def new(library_path, symbol_name, output_path):
    spreadsheet = Spreadsheet()
    if library_path and symbol_name:
        spreadsheet.add_defaults(library_path, symbol_name)

    spreadsheet.write(output_path)


def generate(spreadsheet_path, output_path):
    spreadsheet = Spreadsheet()
    spreadsheet.read(spreadsheet_path)
    spreadsheet.write_symbols(output_path)


def main():
    parser = ArgumentParser(
        prog="kicad-symbol-templater",
        description="Derive KiCad symbol library from a common template",
    )

    subparsers = parser.add_subparsers(help="commands:", dest="command")

    new_parser = subparsers.add_parser(
        "new", help="Create a new spreadsheet from a KiCad symbol"
    )
    new_parser.add_argument(
        "-l",
        "--library",
        help="Symbol library to extract template symbol from",
    )
    new_parser.add_argument(
        "-s",
        "--symbol",
        help="Name of symbol to extract from provided library for templating",
    )
    new_parser.add_argument(
        "-o", "--output", required=True, help="File to output spreadsheet to"
    )

    generate_parser = subparsers.add_parser(
        "generate", help="Generate KiCad symbol library from spreadsheet"
    )
    generate_parser.add_argument(
        "-i", "--input", required=True, help="Path to input spreadsheet with parameters"
    )
    generate_parser.add_argument(
        "-o", "--output", required=True, help="File to output KiCad symbol library to"
    )

    args = parser.parse_args()

    if args.command == "new":
        new(library_path=args.library, symbol_name=args.symbol, output_path=args.output)
    elif args.command == "generate":
        generate(
            spreadsheet_path=args.input,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()
