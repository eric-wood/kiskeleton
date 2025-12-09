from kiutils.symbol import SymbolLib, Symbol as KiSymbol
from symbol import Symbol
import csv


class Spreadsheet:
    symbols = []

    def __init__(self, template_symbol: KiSymbol) -> None:
        self.template_symbol = template_symbol

    def write(self, path: str):
        # TODO: find the intersection of the properties of all symbols
        field_names = ["name"]
        for prop in self.template_symbol.properties:
            field_names.append(prop.key)

        with open(path, "w") as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()
            for symbol in self.symbols:
                writer.writerow({"name": symbol.name(), **symbol.properties})

    def read(self, path: str):
        with open(path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = Symbol(self.template_symbol)
                name = row.pop("name")
                symbol.set_name(name)
                symbol.merge_properties(row)
                self.symbols.append(symbol)

    def write_symbols(self, path: str):
        library = SymbolLib(filePath=path)
        library.symbols = [s.symbol for s in self.symbols]
        library.to_file()

    def add_defaults(self):
        symbol = Symbol(self.template_symbol)
        symbol.set_name(self.template_symbol.entryName)
        self.symbols.append(symbol)
