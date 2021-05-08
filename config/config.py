LEAGUE = 'ultimatum'
POESESSID = '0e2e8a74d772f6b87a72240b23db976b'

POST_URL = f'https://www.pathofexile.com/api/trade/exchange/{LEAGUE}'
GET_URL = 'https://www.pathofexile.com/api/trade/fetch'
PUBLIC_STASH_URL = 'http://www.pathofexile.com/api/public-stash-tabs'

POE_NINJA_LANG = 'en'
POE_NINJA_WTV = '421b35051547a888e1390ffbd9aa7428'
POE_NINJA_LADDER = 'exp'
POE_NINJA_BUILD_OVERVIEW_URL = f'https://poe.ninja/api/data/{POE_NINJA_WTV}/getbuildoverview'
POE_NINJA_STATS_URL = 'https://poe.ninja/api/Data/GetStats'
POE_NINJA_ITEM_OVERVIEW_URL = 'https://poe.ninja/api/data/ItemOverview'
POE_NINJA_CURRENCY_OVERVIEW_URL = 'https://poe.ninja/api/data/CurrencyOverview'
POE_NINJA_UNIQUE_ITEM_TYPES = (
    'UniqueWeapon',
    'UniqueArmour',
    'UniqueAccessory',
    'UniqueFlask',
    'UniqueJewel',
    'UniqueMap'
)
# mapping from POENinja categories to stash API categories
POE_NINJA_CATEGORY_MAP = {
    'UniqueAccessory': 'accessories',
    'UniqueArmour': 'armour',
    'UniqueFlask': 'flasks',
    'UniqueJewel': 'jewels',
    'UniqueMap': 'maps',
    'UniqueWeapon': 'weapons',
}

DATA_DIR = f'./data/{LEAGUE}'

DEFAULT_HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
}

UNIQUES_BLACKLIST = (
    'Watcher\'s Eye',
    'Glorious Vanity',
)

class _TwoWayDict:
    def __init__(self, iterable):
        self._dict = {}
        for k, v in iterable:
            self._dict[k] = v
            self._dict[v] = k
    
    def __getitem__(self, key):
        return self._dict[key]
    
    def __setitem__(self, key, obj):
        self._dict[key] = obj
        self._dict[obj] = key

CURRENCIES_KV = {
    'alt': 'Orb of Alteration',
    'fusing': 'Orb of Fusing',
    'alch': 'Orb of Alchemy',
    'chaos': 'Chaos Orb',
    'gcp': 'Gemcutter\'s Prism',
    'exalted': 'Exalted Orb',
    'chrome': 'Chromatic Orb',
    'jewellers': 'Jeweller\'s Orb',
    'engineers': 'Engineer\'s Orb',
    'infused-engineers-orb': 'Infused Engineer\'s Orb',
    'chance': 'Orb of Chance',
    'chisel': 'Cartographer\'s Chisel',
    'scour': 'Orb of Scouring',
    'blessed': 'Blessed Orb',
    'regret': 'Orb of Regret',
    'regal': 'Regal Orb',
    'divine': 'Divine Orb',
    'vaal': 'Vaal Orb',
    'annul': 'Orb of Annulment',
    'orb-of-binding': 'Orb of Binding',
    'ancient-orb': 'Ancient Orb',
    'orb-of-horizons': 'Orb of Horizons',
    'harbingers-orb': 'Harbinger\'s Orb',
    'wisdom': 'Scroll of Wisdom',
    'portal': 'Portal Scroll',
    'scrap': 'Armourer\'s Scrap',
    'whetstone': 'Blacksmith\'s Whetstone',
    'bauble': 'Glassblower\'s Bauble',
    'transmute': 'Orb of Transmutation',
    'aug': 'Orb of Augmentation',
    'mirror': 'Mirror of Kalandra',
    'eternal': 'Eternal Orb',
    'p': 'Perandus Coin',
    'rogues-marker': 'Rogue\'s Marker',
    'silver': 'Silver Coin',
    'crusaders-exalted-orb': 'Crusader\'s Exalted Orb',
    'redeemers-exalted-orb': 'Redeemer\'s Exalted Orb',
    'hunters-exalted-orb': 'Hunter\'s Exalted Orb',
    'warlords-exalted-orb': 'Warlord\'s Exalted Orb',
    'awakeners-orb': 'Awakener\'s Orb',
    'mavens-orb': 'Maven\'s Orb',
    'facetors': 'Facetor\'s Lens',
    'prime-regrading-lens': 'Prime Regrading Lens',
    'secondary-regrading-lens': 'Secondary Regrading Lens',
    'tempering-orb': 'Tempering Orb',
    'tailoring-orb': 'Tailoring Orb',
    'stacked-deck': 'Stacked Deck',
    'ritual-vessel': 'Ritual Vessel',
    'apprentice-sextant': 'Simple Sextant',
    'journeyman-sextant': 'Prime Sextant',
    'master-sextant': 'Awakened Sextant',
    'elevated-sextant': 'Elevated Sextant',
    'orb-of-unmaking': 'Orb of Unmaking',
    'blessing-xoph': 'Blessing of Xoph',
    'blessing-tul': 'Blessing of Tul',
    'blessing-esh': 'Blessing of Esh',
    'blessing-uul-netol': 'Blessing of Uul-Netol',
    'blessing-chayula': 'Blessing of Chayula',
    'veiled-chaos-orb': 'Veiled Chaos Orb',
}

CURRENCIES = _TwoWayDict(CURRENCIES_KV.items())
