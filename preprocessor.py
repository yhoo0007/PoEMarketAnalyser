import os
import json
import re

from config import DATA_DIR, LEAGUE


def get_item_info(item_category, item_name):
    with open(os.path.join(DATA_DIR, 'uniques.json')) as uniques_file:
        uniques = json.load(uniques_file)
        return uniques[item_category][item_name]

def get_mods_mask(item_info):
    explicit_mods_mask = [False] * len(item_info['explicitModifiers'])
    for index, mod in enumerate(item_info['explicitModifiers']):
        for r in mod['ranges']:
            if r['min'] != r['max']:
                explicit_mods_mask[index] = True

    implicit_mods_mask = [False] * len(item_info['implicitModifiers'])
    for index, mod in enumerate(item_info['implicitModifiers']):
        for r in mod['ranges']:
            if r['min'] != r['max']:
                implicit_mods_mask[index] = True

    return explicit_mods_mask, implicit_mods_mask

def exclude_mods(item_info, explicit_mods_mask, implicit_mods_mask):
    explicit_modifiers = [mod for mask, mod in zip(explicit_mods_mask, item_info['explicitModifiers']) if mask]
    implicit_modifiers = [mod for mask, mod in zip(implicit_mods_mask, item_info['implicitModifiers']) if mask]
    item_info['explicitModifiers'] = explicit_modifiers
    item_info['implicitModifiers'] = implicit_modifiers
    return item_info

def get_csv_headers(item_info):
    item_mods = [mod['text'] for mod in item_info['explicitModifiers'] + item_info['implicitModifiers']]
    return 'price,' + ','.join(item_mods)

def extract_modifier_values(modifier):
    pattern = '([+-]?)(\d+(?:\.\d+)?)'
    values = []
    for match in re.finditer(pattern, modifier):
        sign, value = match.groups()
        values.append(-float(value) if sign == '-' else float(value))
    return values

def convert_listing_to_csv_row(listing, explicit_mods_mask, implicit_mods_mask):
    price = listing['price']
    explicit_modifiers = [mod for mask, mod in zip(explicit_mods_mask, listing['explicitMods']) if mask]
    implicit_modifiers = [mod for mask, mod in zip(implicit_mods_mask, listing['implicitMods']) if mask]
    explicit_mod_values = [sum(extract_modifier_values(mod)) for mod in explicit_modifiers]
    implicit_mod_values = [sum(extract_modifier_values(mod)) for mod in implicit_modifiers]
    mods_string = ','.join(map(str, explicit_mod_values + implicit_mod_values))
    return f'{price},{mods_string}'

def preprocess(listing_file, listings_dir=None):
    if listings_dir is None:  # no explicit directory provided, try to extract it from file
        listings_dir, listing_file = os.path.split(listing_file)
    item_name = os.path.splitext(listing_file)[0]

    # load listings
    with open(os.path.join(listings_dir, listing_file)) as json_file:
        listings = list(json.load(json_file).values())
        if len(listings) == 0:
            return None
        item_category = listings[0]['category']

    # get item info and find mods to exclude, i.e. mods which have no variables
    item_info = get_item_info(item_category, item_name)
    explicit_mods_mask, implicit_mods_mask = get_mods_mask(item_info)
    item_info = exclude_mods(item_info, explicit_mods_mask, implicit_mods_mask)

    # convert listings to csv rows
    csv_rows = [get_csv_headers(item_info)]
    for listing in listings:
        string = convert_listing_to_csv_row(listing, explicit_mods_mask, implicit_mods_mask)
        csv_rows.append(string)
    return csv_rows

if __name__ == '__main__':
    listings_dir = os.path.join(DATA_DIR, 'listings')
    for _, _, files in os.walk(listings_dir):
        for listing_file in files:
            print('Processing', listing_file)
            csv_rows = preprocess(listing_file, listings_dir)
            item_name = os.path.splitext(listing_file)[0]
            with open(os.path.join(DATA_DIR, 'csv', f'{item_name}.csv'), 'w+') as csv_file:
                for row in csv_rows:
                    csv_file.write(row + '\n')
