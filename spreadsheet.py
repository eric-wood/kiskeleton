from kiutils.symbol import SymbolLib, Symbol as KiSymbol
from symbol import Symbol
import csv

symbol_cache: dict[str, KiSymbol] = dict()


class Spreadsheet:
    symbols = []

    def write(self, path: str):
        field_names = ["name", "template_library", "template_symbol_name"]
        for symbol in self.symbols:
            field_names = [*field_names, *symbol.properties.keys()]

        # dedupe while preserving order
        field_names = list(dict.fromkeys(field_names))

        with open(path, "w") as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            for symbol in self.symbols:
                writer.writerow({"name": symbol.name(), **symbol.properties})

    def read(self, path: str):
        with open(path, "r") as file:
            reader = csv.DictReader(file)
            line = 0
            for row in reader:
                line += 1
                if not validate_row(row=row, path=path, line_number=line):
                    continue

                name = row.pop("name")
                template_symbol_library = row.pop("template_library")
                template_symbol_name = row.pop("template_symbol_name")

                template_symbol = get_symbol(
                    template_symbol_library, template_symbol_name
                )
                symbol = Symbol(template_symbol)
                symbol.set_name(name)
                symbol.merge_properties(row)
                self.symbols.append(symbol)

    def write_symbols(self, path: str):
        library = SymbolLib(filePath=path)
        library.symbols = [s.symbol for s in self.symbols]
        library.to_file()

    def add_defaults(self, template_library=None, template_symbol_name=None):
        if template_library is None or template_symbol_name is None:
            return

        template_symbol = get_symbol(template_library, template_symbol_name)
        symbol = Symbol(template_symbol)
        symbol.set_name(template_symbol.entryName)
        self.symbols.append(symbol)


def get_symbol(library_path: str, symbol_name: str) -> KiSymbol:
    cache_key = "{}-{}".format(library_path, symbol_name)
    if cache_key in symbol_cache:
        return symbol_cache[cache_key]

    symbol = retrieve_symbol(library_path, symbol_name)
    symbol_cache[symbol_name] = symbol

    return symbol


def retrieve_symbol(library_path: str, symbol_name: str) -> KiSymbol:
    library = SymbolLib.from_file(library_path)
    for symbol in library.symbols:
        if symbol.entryName == symbol_name:
            return symbol

    print(
        "Unable to locate symbol {} in library {}; skipping".format(
            symbol_name, library_path
        )
    )


def validate_row(row: dict[str, str], path: str, line_number: int) -> bool:
    if "name" not in row:
        csv_error(
            message='Missing "name" column. Skipping.',
            file=path,
            line_number=line_number,
        )
        return False
    if "template_library" not in row:
        csv_error(
            message='Missing "template_library" column. Skipping.',
            file=path,
            line_number=line_number,
        )
        return False
    if "template_symbol_name" not in row:
        csv_error(
            message='Missing "template_symbol_name" column. Skipping.',
            file=path,
            line_number=line_number,
        )
        return False

    return True


def csv_error(message: str, file: str, line_number: int):
    print("\033[91mERROR\033[0m [{}:{}] {}".format(file, line_number, message))
