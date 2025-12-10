# KiSkeleton 🩻

Derive KiCad symbol libraries from spreadsheets

## The problem

You have a large number of KiCad symbols with differing parameters derived from the same "template" symbol.

You want a single source of truth for these that's easy to manage.

*Example*:

You have 100 different resistors, each with different values, datasheets, footprints, and manufacturer metadata.

Keeping a library of discrete symbols for each variation helps you place these and not sweat backfilling this metadata per project.

This is a task that is much easier to manage from a spreadsheet rather than creating every single part from scratch; after all, they're all the same base resistor symbol!

## Installation

This project uses [uv](https://docs.astral.sh/uv/) to manage stuff.

Install it and then do:

```sh
uv run main.py
```

...and it should all work.

## Usage

There's two phases to using the tool:

- Creating a new spreadsheet from an existing symbol
- Generating a symbol library from the input spreadsheet

### Creating a new spreadsheet

You'll need to point the tool to the symbol you want to derive your spreadsheet from, and tell it where to output it.

This example uses the default resistor symbol as an input:

```sh
uv run main.py new \
  --library /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym \
  --symbol R \
  --output my_cool_new_library.csv
```

This will generate the spreadsheet with a row pre-filled with the properties taken from the existing symbol.
You will now fill this out with all of your parts.

### Generating from the spreadsheet

With the spreadsheet filled out, it's time to generate the symbol library:

```sh
uv run main.py generate \
  --library /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym \
  --symbol R \
  --input my_cool_new_library.csv \
  --output my_cool_new_library.kicad_sym
```

## Roadmap

At this point it's more of a demo than anything else.
But it seems to work.

In the future I'd like to add the following:

- A config file format so the generate command can be run across many spreadsheets without CLI arguments
- Package it as a `uv` tool so cloning the repo isn't necessary
- Much more robust error handling
