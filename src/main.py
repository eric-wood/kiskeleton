from argparse import ArgumentParser
from src.spreadsheet import Spreadsheet
import src.logger
import src.formatter


def new(library_path, symbol_name, output_path):
    spreadsheet = Spreadsheet()
    if library_path and symbol_name:
        spreadsheet.add_defaults(library_path, symbol_name)
    elif library_path and symbol_name is None:
        spreadsheet = Spreadsheet.from_library(library_path)

    spreadsheet.write(output_path)


def generate(spreadsheet_path, output_path):
    spreadsheet = Spreadsheet()
    spreadsheet.read(spreadsheet_path)
    spreadsheet.write_symbols(output_path)


def main():
    parser = ArgumentParser(
        prog="kiskeleton",
        description="Derive and modify KiCad symbol libraries with spreadsheets",
    )

    subparsers = parser.add_subparsers(help="commands:", dest="command")

    new_parser = subparsers.add_parser(
        "new", help="Create a new spreadsheet from a KiCad library or symbol"
    )
    new_parser.add_argument(
        "-l",
        "--library",
        help="Symbol library to convert to spreadsheet",
    )
    new_parser.add_argument(
        "-s",
        "--symbol",
        help="Name of symbol to extract from provided library; if omitted the entire library will be used",
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
    else:
        print("""
  ____________ 
 | Welcome to |
 | KiSkeleton |   .-.
  ‾‾‾‾‾‾‾‾‾‾‾\\|  (o.o)
                  |=|
                 __|__
               //.=|=.\\\\
              // .=|=. \\\\
              \\\\ .=|=. //
               \\\\(_=_)//
                (:| |:)
                 || ||
                 () ()
                 || ||
                 || ||
                ==' '==
        """)
        parser.print_help()


if __name__ == "__main__":
    main()
