from sexpdata import loads, dumps, tosexp, Delimiters, Symbol

# Cool hack to format roughly how KiCad does it taken from the sexpdata Github issues:
# https://github.com/jd-boyd/sexpdata/issues/33

ROUND_2_SYMBOLS = ("at",)


@tosexp.register(float)
def _(obj, **kwds):
    if kwds["car_stack"][-1] in ROUND_2_SYMBOLS:
        _ = round(obj, 2)
        return f"{_:.2f}"
    return str(obj)


BREAK_OPENER_SYMBOLS = (
    "symbol",
    "property",
    "effects",
    "pin",
    "name",
    "number",
    "rectangle",
    "stroke",
    "fill",
)
BREAK_CLOSER_SYMBOLS = ("kicad_symbol_lib", "symbol", "property", "pin", "rectangle")
BREAK_PREFIX_SYMBOLS = ("kicad_symbol_lib",)


def dont_break(car_stack, str_car):
    return str_car == "effects" and car_stack[-1] in ("name", "number")


@tosexp.register(Delimiters)
def _(self, **kwds):
    expr_separator = " "
    exprs_indent = ""
    break_prefix_opener = ""
    break_prefix_closer = ""
    suffix_break = ""

    car = self.I[0]
    if isinstance(car, Symbol):
        str_car = str(car)
        kwds.setdefault("car_stack", [])
        if str_car in BREAK_OPENER_SYMBOLS and not dont_break(
            kwds["car_stack"], str_car
        ):
            exprs_indent = "  "
            break_prefix_opener = "\n" + exprs_indent
        if str_car in BREAK_CLOSER_SYMBOLS:
            break_prefix_closer = "\n" + exprs_indent
        kwds["car_stack"].append(str_car)
        if str_car in BREAK_PREFIX_SYMBOLS:
            suffix_break = "\n"

    exprs = expr_separator.join(tosexp(x, **kwds) for x in self.I)
    indented_exprs = "\n".join(
        exprs_indent + line.rstrip() for line in exprs.splitlines(True)
    )
    indented_exprs = indented_exprs[len(exprs_indent) :]

    if kwds.get("car_stack", None):
        kwds["car_stack"].pop()

    return (
        break_prefix_opener
        + self.__class__.opener
        + indented_exprs
        + break_prefix_closer
        + self.__class__.closer
        + suffix_break
    )
