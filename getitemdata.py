import os
import json

from modules.poeninjaclient import PoeNinjaClient
from config import POE_NINJA_UNIQUE_ITEM_TYPES, POE_NINJA_CATEGORY_MAP, DATA_DIR


if __name__ == '__main__':
    poe_ninja_client = PoeNinjaClient()

    unique_items = {}
    for item_type in POE_NINJA_UNIQUE_ITEM_TYPES:
        print('Fetching item type:', item_type)
        items = poe_ninja_client.get_item_data(item_type)
        unique_items[POE_NINJA_CATEGORY_MAP[item_type]] = items

    with open(os.path.join(DATA_DIR, 'uniques.json'), 'w+') as json_file:
        json.dump(unique_items, json_file, indent=2)
