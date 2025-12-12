from kiutils.symbol import Symbol as KiSymbol
from kiutils.items.common import Property


class Symbol:
    properties: dict[str, str] = {}

    def __init__(self, symbol: KiSymbol) -> None:
        self.symbol = symbol
        for prop in self.symbol.properties:
            self.properties[prop.key] = prop.value

    def merge_properties(self, props: dict[str, str]):
        self.properties = self.properties | props
        self.symbol.properties = [
            Property(k, self.properties[k]) for k in self.properties
        ]

    def set_name(self, name: str):
        self.symbol.entryName = name

        # units are symbols within the symbol, and their prefix has to match the parent name
        for unit in self.symbol.units:
            unit.entryName = unit.entryName.replace(unit.entryName, name)

    def name(self):
        self.symbol.entryName
