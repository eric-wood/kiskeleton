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

        self.symbol_names = set()
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

                cache_key = template_cache_key(
                    template_symbol_library, template_symbol_name
                )
                self.templates[cache_key] = template_symbol
                symbol = Symbol(
                    template_library=template_symbol_library,
                    template_name=template_symbol_name,
                    properties=deepcopy(template_symbol.properties),
                )
                symbol.set_name(name)
                symbol.merge_properties(row)
                self.symbols.append(symbol)
                self.symbol_names.add(symbol.name)

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
        library_templates = []
        library_symbols = []

        # directly map symbols to their templates so we can easily process the relationships
        symbols_by_template: dict[str, list[Symbol]] = {}
        for symbol in self.symbols:
            cache_key = template_cache_key(
                symbol.template_library, symbol.template_name
            )
            symbols = symbols_by_template.get(cache_key, [])
            symbols.append(symbol)
            symbols_by_template[cache_key] = symbols

        for template_key in symbols_by_template:
            template = self.templates[template_key]
            template.extends = None
            symbols = symbols_by_template[template_key]

            if len(symbols) > 1:
                # more than one symbol uses the template, so use derived symbols to define it
                for symbol in symbols:
                    symbol.extends = template.name
                    if template.name == symbol.name:
                        # this is an edge case from importing a symbol library that uses derived symbols;
                        # the "root" symbol others are derived from ends up in the spreadsheet.
                        # if the names match it's pretty safe to say we just want to extend it
                        template.merge_properties(symbol.properties_dict())
                    else:
                        library_symbols.append(symbol)

                library_templates.append(template)
            else:
                # only one symbol uses the template, so just clone/override it to avoid bloat
                symbol = symbols[0]
                new_symbol = deepcopy(template)
                new_symbol.merge_properties(symbol)
                library_symbols.append(symbol)

        # kicad is picky about symbol order; if you extend a symbol, that symbol needs to be first in the file
        library.symbols = [*library_templates, *library_symbols]
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
    cache_key = template_cache_key(library_path, symbol_name)
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


def template_cache_key(library: str, name: str) -> str:
    return "{}-{}".format(library, name)


def csv_error(message: str, line_number: int):
    logging.error("line {}: {}".format(line_number, message))
