import heapq
import os
import json
import time
import re
import itertools
from tqdm import tqdm

from config import PUBLIC_STASH_URL, POE_NINJA_STATS_URL, DEFAULT_HEADERS, DATA_DIR, LEAGUE
from modules.poeninjaclient import PoeNinjaClient
from modules.requestclient import RequestClient
from currencyexchange import CurrencyExchange


N = 30  # number of uniques to scan for
DUMP_THRESHOLD = 20  # number of items in dict before updating to disk

poe_ninja_client = PoeNinjaClient()
request_client = RequestClient()
currency_exchange = CurrencyExchange()

def get_next_change_id():
    return request_client.get(POE_NINJA_STATS_URL).json()['next_change_id']

def clean_currency(currency):
    if currency == 'exa':
        return 'exalted'
    return currency

def extract_price(note):
    pattern = '^~(?:price|b\/o) (\d+(?:\.\d+)?) (\w+)$'
    match = re.search(pattern, note)
    if match:
        amount, currency = match.groups()
        currency = clean_currency(currency)
        try:
            price = round(float(amount) * currency_exchange.get_exchange_rate(currency, 'chaos'), 2)
            return price
        except Exception as e:
            print(e)
    return None

def clean_item(item_json):
    return {
        'name': item_json['name'],
        'category': item_json['extended']['category'],
        'corrupted': item_json.get('corrupted', False),
        'league': item['league'],
        'properties': item.get('properties', []),
        'explicitMods': item.get('explicitMods', []),
        'implicitMods': item.get('implicitMods', [])
    }

def update_file(name, instances):
    file_path = os.path.join(DATA_DIR, 'listings', f'{name}.json')
    
    # Update existing file if possible, else write instances as new file
    if os.path.exists(file_path):
        with open(file_path) as json_file:
            json_obj = json.load(json_file)
        json_obj.update(instances)
    else:
        json_obj = instances
    
    # Dump to file
    with open(file_path, 'w+') as json_file:
        json.dump(json_obj, json_file, indent=2)

def item_is_acceptable(item, acceptable_items):
    return (
        item['league'].casefold() == LEAGUE.casefold() and
        'note' in item and
        item['identified'] and
        item['name'] in acceptable_items
    )

if __name__ == '__main__':
    # get most used uniques
    print(f'Fetching top {N} unique items')
    top_n = poe_ninja_client.get_unique_item_use(n=N)
    unique_item_names = set((itemuse.item.name for itemuse in top_n))

    # listen for details for top N items using public stash API
    print('Listening to public stash API')
    next_change_id = get_next_change_id()
    unique_item_instances = {
        item: {}
    for item in unique_item_names}
    try:
        while True:
            # get from stash API
            last_request_time = time.time()
            next_request_time = last_request_time + 0.51
            json_obj = request_client.get(
                PUBLIC_STASH_URL, params={'id': next_change_id}, headers=DEFAULT_HEADERS
            ).json()

            # parse response, add relevant items to collection
            processed_items = 0
            accepted_items = 0
            dumps = 0
            processing_time = time.time()
            stashes = json_obj['stashes']
            for item in itertools.chain.from_iterable(map(lambda s: s['items'], stashes)):
                if (item_is_acceptable(item, unique_item_names)):
                    price = extract_price(item['note'])
                    if price is not None:
                        instance = clean_item(item)
                        instance['price'] = price
                        item_name = item['name']
                        instances = unique_item_instances[item_name]
                        instances[item['id']] = instance
                        if len(instances) > DUMP_THRESHOLD:  # dump item instances to disk
                            update_file(item_name, instances)
                            unique_item_instances[item_name] = {}
                            dumps += 1
                        accepted_items += 1
                processed_items += 1
            processing_time = time.time() - processing_time

            # Update NCID, throttle rate if necessary
            current_time = time.time()
            print(f'Processed: ({processed_items};{accepted_items};{dumps}) items in {round(processing_time * 1000, 2)}ms')
            if next_request_time <= current_time:
                next_change_id = get_next_change_id()
            else:
                next_change_id = json_obj['next_change_id']
                delay = next_request_time - current_time
                time.sleep(max(delay, 0))
    except (KeyboardInterrupt, ConnectionError):
        print('\nKeyboard Interrupt/Connection Error; dumping to disk')
        for item_name, instances in tqdm(unique_item_instances.items(), ncols=50, unit='file'):
            update_file(item_name, instances)
