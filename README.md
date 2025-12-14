# KiSkeleton 🩻

Derive and modify KiCad symbol libraries with spreadsheets

## The problem

You have a large number of KiCad symbols with differing parameters derived from existing symbols.

You want a single source of truth for these that's easy to manage.

*Example*:

You have 100 different resistors, each with different values, datasheets,
footprints, and manufacturer metadata.

Keeping a library of discrete symbols for each variation helps you place these
and not sweat backfilling this metadata per project.

This is a task that is much easier to manage from a spreadsheet rather than
creating every single part from scratch; after all, they're all the same base resistor symbol!

## Installation

This project uses [uv](https://docs.astral.sh/uv/) to manage stuff.

You can run it directly without installing with `uvx`:

```sh
uvx kiskeleton
```

### Manual install

Clone this repo somewhere, then do:

```sh
uv tool install -e PATH_TO_CLONED_REPO
```

Now you can run it from wherever:

```sh
uv run kiskeleton
```

## Usage

There's two phases to using the tool:

- Creating a new spreadsheet (possibly from an existing library/symbol)
- Generating a symbol library from the input spreadsheet

### Creating a new spreadsheet

The `new` command helps you scaffold your spreadsheet.
With no options provided, a blank spreadsheet with the minimum required
fields is created.

You can also pass in the `library` and `symbol` options, which let you bootstrap
it from a full existing library, or an existing symbol.

This example uses the default resistor symbol as an input:

```sh
kiskeleton new \
  --library /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym \
  --symbol R \
  --output my_cool_new_library.csv
```

This will generate the spreadsheet with a row pre-filled with the properties
taken from the existing symbol.

You will now fill this out with all of your parts.

### Generating from the spreadsheet

With the spreadsheet filled out, it's time to generate the symbol library:

```sh
kiskeleton generate \
  --input my_cool_new_library.csv \
  --output my_cool_new_library.kicad_sym
```

### Required columns

The `name`, `template_library`, and `template_symbol_name` columns are required:

- `name` is the name of the symbol in the new library
- `template_library` is the library to pull our "template" symbol from
- `template_symbol_name` is the symbol within the library to base our new symbol off of

Any new properties that exist on the spreadsheet but not in the template symbol
will be added and marked as hidden by default. If you wish to style/position
these fields make sure they exist on your template symbols already (the value will be overwritten).
