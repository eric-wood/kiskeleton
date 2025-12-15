import logging
import csv
from copy import deepcopy
from src.symbol import Symbol
from src.library import Library
import os.path
from typing import Self

symbol_cache: dict[str, Symbol] = dict()


class Spreadsheet:
    symbols = []
    templates = {}

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
                properties = {}
                for prop in symbol.properties:
                    properties[prop] = symbol.properties[prop].value
                template = {
                    "template_library": symbol.template_library,
                    "template_symbol_name": symbol.template_name,
                }

                writer.writerow({"name": symbol.name, **properties, **template})

    def read(self, path: str):
        if not os.path.isfile(path):
            logging.error("file not found %s", path)
            return

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
                if template_symbol is None:
                    logging.warning(
                        "Missing unable to locate template symbol for row %d, skipping",
                        line,
                    )
                    continue

                self.templates[template_symbol_name] = template_symbol
                symbol = Symbol(
                    template_library=template_symbol_library,
                    template_name=template_symbol_name,
                )
                symbol.set_name(name)
                symbol.merge_properties(row)
                self.symbols.append(symbol)

    @classmethod
    def from_library(cls, library_path: str) -> Self:
        library = Library.from_file(library_path)
        spreadsheet = cls()
        spreadsheet.symbols = library.symbols
        for symbol in spreadsheet.symbols:
            symbol.template_library = library_path
            if symbol.extends is None:
                symbol.template_name = symbol.name

        return spreadsheet

    def write_symbols(self, path: str):
        library = Library.new()
        for template_name in self.templates:
            template = self.templates[template_name]
            template.extends = None
            template.set_name("template_{}".format(template_name))
            library.symbols.append(template)

        for symbol in self.symbols:
            symbol.extends = "template_{}".format(symbol.template_name)
            library.symbols.append(symbol)

        library.to_file(path)

    def add_defaults(self, template_library=None, template_symbol_name=None):
        if template_library is None or template_symbol_name is None:
            return

        template_symbol = deepcopy(get_symbol(template_library, template_symbol_name))
        if template_symbol is None:
            return

        template_symbol.template_library = template_library
        template_symbol.template_name = template_symbol_name
        self.symbols.append(template_symbol)


def get_symbol(library_path: str, symbol_name: str) -> Symbol | None:
    cache_key = "{}-{}".format(library_path, symbol_name)
    if cache_key in symbol_cache:
        return symbol_cache[cache_key]

    symbol = retrieve_symbol(library_path, symbol_name)
    if symbol is None:
        return

    symbol_cache[symbol_name] = symbol

    return symbol


def retrieve_symbol(library_path: str, symbol_name: str) -> Symbol | None:
    library = Library.from_file(library_path)

    for symbol in library.symbols:
        if symbol.name == symbol_name:
            return symbol

    logging.error(
        "Unable to locate symbol {} in library {}; skipping".format(
            symbol_name, library_path
        )
    )


def validate_row(row: dict[str, str], path: str, line_number: int) -> bool:
    if "name" not in row:
        csv_error(
            message='Missing "name" column. Skipping.',
            line_number=line_number,
        )
        return False
    if "template_library" not in row:
        csv_error(
            message='Missing "template_library" column. Skipping.',
            line_number=line_number,
        )
        return False
    if "template_symbol_name" not in row:
        csv_error(
            message='Missing "template_symbol_name" column. Skipping.',
            line_number=line_number,
        )
        return False

    return True


def csv_error(message: str, line_number: int):
    logging.error("line {}: {}".format(line_number, message))
