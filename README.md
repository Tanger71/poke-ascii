# Pokémon ASCII Art Generator

A CLI tool that fetches Pokémon data from [PokeAPI](https://pokeapi.co/), converts their official artwork into Braille-based ASCII art, and displays it in your terminal.

## Features
- **Bilingual Display**: Shows English and Japanese names.
- **Region Filtering**: Select random Pokémon from specific regions (Kanto, Johto, etc.).

## Prerequisites
- **Python 3.x**
- **pip** (Python package manager)

## Setup

### 1. Set Up a Virtual Environment (Recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
```

### 2. Install Dependencies
```bash
pip install requests Pillow charset-normalizer
```

## Usage

### Running with Python
```bash
python3 poke-ascii.py [ID or Name] [Options]
```

### Options
- `pokemon`: (Optional) ID or Name of the Pokémon.
- `--hide-name`: Hide the name footer from the output.
- `--region`: Select a random Pokémon from a specific region.
  - Choices: `kanto`, `johto`, `hoenn`, `sinnoh`, `unova`, `kalos`, `alola`, `galar`, `hisui`, `paldea`.
- `-h, --help`: Show the help message.

### Examples
- **Random Pokémon**: `python3 poke-ascii.py`
- **Specific Pokémon**: `python3 poke-ascii.py pikachu`
- **Kanto Random**: `python3 poke-ascii.py --region kanto`
- **Hide Name**: `python3 poke-ascii.py 151 --hide-name`

## Building a Standalone Executable
To package the script into a single, portable binary:
```bash
./.venv/bin/pyinstaller --onefile poke-ascii.py
```
The resulting executable will be in the `dist/` directory.

### Running the Binary
```bash
./dist/poke-ascii --region johto
```
