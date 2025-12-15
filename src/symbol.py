from typing import Self
from dataclasses import dataclass, field
from sexpdata import Symbol as SexprSymbol


@dataclass
class SymbolProperty:
    name: str = ""
    value: str = ""
    params: list = field(default_factory=lambda: [])

    @classmethod
    def from_sexpr(cls, sexpr: list) -> Self:
        _, name, value, *params = sexpr

        symbol = cls(name=name, value=value, params=params)
        return symbol

    @classmethod
    def default(cls, name: str, value: str) -> Self:
        params = [
            [
                SexprSymbol("effects"),
                [
                    SexprSymbol("hide"),
                    SexprSymbol("yes"),
                ],
            ]
        ]
        return cls(name=name, value=value, params=params)

    def to_sexpr(self):
        return [SexprSymbol("property"), self.name, self.value, *self.params]


@dataclass
class Symbol:
    name: str = ""
    extends: str | None = None
    manifest: list[SexprSymbol] = field(default_factory=lambda: [])
    properties: dict[str, SymbolProperty] = field(default_factory=lambda: {})
    symbols: list[Self] = field(default_factory=lambda: [])
    template_library: str | None = None
    template_name: str | None = None

    @classmethod
    def from_sexpr(cls, sexpr: list) -> Self:
        _, name, *props = sexpr

        symbol = cls(name=name)

        for expr in props:
            token = expr[0]
            match str(token):
                case "property":
                    prop = SymbolProperty.from_sexpr(expr)
                    symbol.properties[prop.name] = prop
                case "symbol":
                    symbol.symbols.append(cls.from_sexpr(expr))
                case "extends":
                    symbol.extends = expr[1]
                    symbol.template_name = symbol.extends
                case _:
                    symbol.manifest.append(expr)

        return symbol

    def set_name(self, name: str):
        for symbol in self.symbols:
            new_name = symbol.name.replace(self.name, name)
            symbol.set_name(new_name)

        self.name = name

    def merge_properties(self, props: dict[str, str]):
        for prop in props:
            value = props[prop]
            if prop in self.properties:
                self.properties[prop].value = value
            else:
                new_prop = SymbolProperty.default(name=prop, value=value)
                self.properties[prop] = new_prop

    def to_sexpr(self):
        symbols = [s.to_sexpr() for s in self.symbols]
        properties = [self.properties[p].to_sexpr() for p in self.properties]
        extends = []
        if self.extends is not None:
            extends = [[SexprSymbol("extends"), self.extends]]

        return [
            SexprSymbol("symbol"),
            self.name,
            *extends,
            *self.manifest,
            *properties,
            *symbols,
        ]
