import heapq
import re
import os
import json

from config import (
    POE_NINJA_UNIQUE_ITEM_TYPES,
    POE_NINJA_BUILD_OVERVIEW_URL,
    LEAGUE,
    POE_NINJA_LADDER,
    POE_NINJA_LANG,
    POE_NINJA_ITEM_OVERVIEW_URL,
    POE_NINJA_CURRENCY_OVERVIEW_URL,
    DATA_DIR,
    UNIQUES_BLACKLIST
)
from modules.requestclient import RequestClient
from .itemuse import ItemUse
from .item import Item


class PoeNinjaClient:
    def __init__(self):
        self.request_client = RequestClient()
    
    def get_league(self):
        return ''.join(map(lambda string: string.capitalize(), LEAGUE.split(' ')))
    
    def flatten_lines(self, lines):
        ret = []
        for sublist in lines:
            if not isinstance(sublist, list):
                return lines
            ret += sublist
        return ret

    def get_unique_item_use(self, n=None):
        json_obj = self.request_client.get(
            POE_NINJA_BUILD_OVERVIEW_URL,
            params={
                'overview': LEAGUE,
                'type': POE_NINJA_LADDER,
                'language': POE_NINJA_LANG,
            }
        ).json()
        unique_items = json_obj['uniqueItems']
        unique_item_use = json_obj['uniqueItemUse']
        combined = []
        for index, item in enumerate(unique_items):
            if item['name'] not in UNIQUES_BLACKLIST:
                heapq.heappush(
                    combined,
                    ItemUse(len(unique_item_use[str(index)]), Item(item['name'], item['type']))
                )
        if n is not None:
            if n >= 0:
                return heapq.nlargest(n, combined)
            return heapq.nsmallest(-n, combined)
        return combined

    def extract_ranges(self, string):
        # matches constants and ranges in 4 groups:
        # 1. sign (optional)
        # 2. ignore
        # 3. lower number (possibly a negative number)
        # 4. upper number (optional)
        pattern = '([+-]?)(\()?([+-]?\d+(?:\.\d+)?)(?(2)-(\d+(?:\.\d+)?)|(?!\)))'
        ranges = []
        for match in re.finditer(pattern, string):
            sign, _, lower, upper = match.groups()
            lower = float(lower)
            upper = float(upper) if upper is not None else lower  # empty 'upper' indicates constant
            ranges.append({
                'min': -lower if sign == '-' else lower,
                'max': -upper if sign == '-' else upper,
            })
        return ranges

    def get_item_data(self, type):
        json_obj = self.request_client.get(
            POE_NINJA_ITEM_OVERVIEW_URL,
            params={
                'league': self.get_league(),
                'type': type,
                'language': POE_NINJA_LANG,
            }
        ).json()
        items = {}
        for item in self.flatten_lines(json_obj['lines']):
            if not item['detailsId'].endswith('-relic'):  # filter out relic items
                for modifier in item['explicitModifiers']:
                    modifier['ranges'] = self.extract_ranges(modifier['text'])
                for modifier in item['implicitModifiers']:
                    modifier['ranges'] = self.extract_ranges(modifier['text'])
                items[item['name']] = {
                    'detailsId': item['detailsId'],
                    'name': item['name'],
                    'explicitModifiers': item['explicitModifiers'],
                    'implicitModifiers': item['implicitModifiers'],
                    'links': item.get('links', None),
                    'mapTier': item.get('mapTier', None),
                }
        return items

    def get_currency_data(self):
        json_obj = self.request_client.get(
            POE_NINJA_CURRENCY_OVERVIEW_URL,
            params={
                'league': self.get_league(),
                'type': 'Currency',
                'language': POE_NINJA_LANG,
            }
        ).json()
        currencies_chaos_val = {}
        for currency in self.flatten_lines(json_obj['lines']):
            currencies_chaos_val[currency['currencyTypeName']] = float(currency['chaosEquivalent'])
        currencies_chaos_val['Chaos Orb'] = 1.0
        return currencies_chaos_val
