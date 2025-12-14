import os.path
import logging
from typing import Self
from dataclasses import dataclass, field
from src.symbol import Symbol
from sexpdata import loads, dump, Symbol as SexprSymbol


@dataclass
class Library:
    manifest: list[SexprSymbol] = field(default_factory=lambda: [])
    symbols: list[Symbol] = field(default_factory=lambda: [])

    @classmethod
    def new(cls) -> Self:
        return cls(
            manifest=[
                SexprSymbol("kicad_symbol_lib"),
                [SexprSymbol("version"), 20231120],
                [SexprSymbol("generator"), "None"],
                [SexprSymbol("generator_version"), "8.0"],
            ]
        )

    @classmethod
    def from_str(cls, contents: str) -> Self:
        symbols = []
        manifest = []
        for expr in loads(contents):
            token = expr[0]
            if token == SexprSymbol("symbol"):
                symbols.append(Symbol.from_sexpr(expr))
            else:
                manifest.append(expr)

        return cls(symbols=symbols, manifest=manifest)

    @classmethod
    def from_file(cls, path: str) -> Self:
        if not os.path.isfile(path):
            logging.error("library not found %s", path)

        with open(path) as file:
            return cls.from_str(file.read())

    def to_sexpr(self):
        symbols = [s.to_sexpr() for s in self.symbols]
        return [*self.manifest, *symbols]

    def to_file(self, path: str):
        with open(path, "w") as file:
            dump(self.to_sexpr(), file)
