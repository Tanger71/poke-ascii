#!/usr/bin/env python3
import warnings
# Suppress the character detection warning at the very top
warnings.filterwarnings("ignore", ".*character detection.*")

import requests
import random
import sys
import argparse
from PIL import Image, ImageOps, ImageFilter
from io import BytesIO

# Region name to (start_id, end_id) mapping
REGIONS = {
    "kanto": (1, 151),
    "johto": (152, 251),
    "hoenn": (252, 386),
    "sinnoh": (387, 493),
    "unova": (494, 649),
    "kalos": (650, 721),
    "alola": (722, 809),
    "galar": (810, 898),
    "hisui": (899, 905),
    "paldea": (906, 1025)
}

def get_pokemon_data(pokemon_id=None, region=None):
    # If a region is specified and no specific ID is provided, pick a random one from that region
    if not pokemon_id:
        if region and region.lower() in REGIONS:
            start, end = REGIONS[region.lower()]
            pokemon_id = random.randint(start, end)
        else:
            # Default to all currently supported Pokémon in PokeAPI (approx 1025)
            pokemon_id = random.randint(1, 1025)

    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        # Use stderr for the status message
        print(f"\033[2mFetching data for '{pokemon_id}'...\033[0m", end="\r", file=sys.stderr, flush=True)

        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            raise ValueError(f"Pokemon '{pokemon_id}' not found.")
        response.raise_for_status()

        data = response.json()

        # Using 'official-artwork' for better outlines
        sprites = data.get('sprites', {})
        other = sprites.get('other', {})
        official_artwork = other.get('official-artwork', {})
        img_url = official_artwork.get('front_default')

        if not img_url:
            # Fallback to default front sprite if official artwork is missing
            img_url = sprites.get('front_default')

        if not img_url:
            raise ValueError(f"No image found for '{pokemon_id}'.")

        # Fetch species data for translated names
        species_url = data.get('species', {}).get('url')
        if species_url:
            species_response = requests.get(species_url, timeout=10)
            species_response.raise_for_status()
            species_data = species_response.json()

            # Find English and Japanese (ja-hrkt) names
            names = species_data.get('names', [])
            en_name = next((n['name'] for n in names if n['language']['name'] == 'en'), data.get('name', str(pokemon_id)))
            ja_name = next((n['name'] for n in names if n['language']['name'] == 'ja-hrkt'), "")
        else:
            en_name = data.get('name', str(pokemon_id))
            ja_name = ""

        img_response = requests.get(img_url, timeout=10)
        img_response.raise_for_status()

        # Clear the "Fetching..." line from stderr
        print(" " * 40, end="\r", file=sys.stderr, flush=True)

        return Image.open(BytesIO(img_response.content)), en_name, ja_name

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error: Could not connect to PokeAPI. ({e})")
    except Exception as e:
        raise e

def image_to_braille(img, width=80):
    # 1. Resize and Grayscale
    aspect_ratio = img.height / img.width
    # Braille characters are roughly 2:1 height/width, so we adjust height
    height = int(width * aspect_ratio * 0.5) 
    img = img.resize((width * 2, height * 4)).convert('L')

    # 2. Outline / Edge Detection
    # Using FIND_EDGES creates the "outline" look
    img = img.filter(ImageFilter.FIND_EDGES)
    # Thresholding to make it strictly Black & White
    img = img.point(lambda x: 255 if x > 30 else 0).convert('1')

    # Crop to content to remove deadspace
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    pixels = img.load()
    braille_output = ""

    # 3. Map 2x4 pixel blocks to Unicode Braille (U+2800 - U+28FF)
    # Loop over the image in 2x4 blocks
    for y in range(0, img.height, 4):
        line = ""
        for x in range(0, img.width, 2):
            # Braille dot mapping (standard bit-order)
            dot_map = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (0,3), (1,3)]
            byte = 0
            for i, (dx, dy) in enumerate(dot_map):
                # Check bounds for each dot in the 2x4 block
                if x + dx < img.width and y + dy < img.height:
                    if pixels[x + dx, y + dy]:
                        byte |= (1 << i)
            line += chr(0x2800 + byte)
        braille_output += line.rstrip(chr(0x2800)) + "\n"

    return braille_output.strip("\n")

# Run the process
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pokémon ASCII Art Generator")
    parser.add_argument("pokemon", nargs="?", help="Pokémon ID or Name (random if omitted)")
    parser.add_argument("--hide-name", action="store_true", help="Hide the Pokémon name from the output")
    parser.add_argument("--region", choices=list(REGIONS.keys()), help="Select a random Pokémon from a specific region")
    args = parser.parse_args()

    try:
        image, name, ja_name = get_pokemon_data(args.pokemon, args.region)

        print(image_to_braille(image, width=60))

        if not args.hide_name:
            # Low profile display: Dimmed text (using ANSI escape code \033[2m)
            if ja_name:
                print(f"\033[2m   {name} / {ja_name}\033[0m\n")
            else:
                print(f"\033[2m   {name}\033[0m\n")

    except (ValueError, ConnectionError) as e:
        print(f"\033[91mError:\033[0m {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\033[91mUnexpected Error:\033[0m {e}", file=sys.stderr)
        sys.exit(1)
