import time

from modules.requestclient import RequestClient
from modules.poeninjaclient import PoeNinjaClient
from config import POESESSID, POST_URL, GET_URL, DEFAULT_HEADERS, CURRENCIES, CURRENCIES_KV


class CurrencyExchange:
    def __init__(self, cache_expiry=3600):
        self.post_url = POST_URL
        self.get_url = GET_URL
        self.request_client = RequestClient()
        self.headers = DEFAULT_HEADERS
        self.cookies = {'cookie': POESESSID}
        self.source = None
        self.poe_ninja_client = PoeNinjaClient()
        self.cache_expiry = cache_expiry
        self.last_refresh = None
        self.exchange_rates = {
            currency_key: {}
        for currency_key in CURRENCIES_KV}

    def refresh_required(self):
        return self.last_refresh + self.cache_expiry <= time.time()

    def cache_valid(self, want, have, source):
        return (
            want in self.exchange_rates[have] and
            source == self.source and
            not self.refresh_required()
        )

    def get_exchange_rate(self, have, want, refresh=False, source='ninja'):
        # Exchanging to itself is always 1:1
        if have == want:
            return 1

        # Return from cache if fetching is not required
        if not refresh and self.cache_valid(want, have, source):
            return self.exchange_rates[have][want]

        # Fetch info from source and cache it
        if source == 'tradeapi':
            exchange_rate = self.fetch_exchange_rate_trade_api(have, want)
        elif source == 'ninja':
            exchange_rate = self.fetch_exchange_rate_poe_ninja(have, want)
        else:
            raise ValueError('Invalid arguments provided')
        self.source = source
        self.last_refresh = time.time()
        self.exchange_rates[have][want] = exchange_rate

        return exchange_rate

    def fetch_exchange_rate_trade_api(self, have, want):
        # send POST request to get listing IDs
        QUERY = {
            'exchange': {
                'status': {'option': 'online'},
                'have': [have],
                'want': [want],
            }
        }
        json_obj = self.request_client.post(
            self.post_url,
            json=QUERY,
            headers=self.headers,
            cookies=self.cookies
        ).json()
        # form GET requests
        results = json_obj['result']
        query_id = json_obj['id']
        requests = []
        for index in range(0, min(2, len(results)), 10):  # get at most 20(2x10) listings
            results_str = ','.join(results[index: min(index + 10, len(results))])
            url = f'{self.get_url}/{results_str}?query={query_id}&exchange'
            requests.append({
                'url': url,
                'kwargs': {
                    'headers': self.headers,
                    'cookies': self.cookies
                }
            })
        # send GET requests
        return_objs = [
            obj.get('listing', {}).get('price', {}) for sublist in self.request_client.get_map(
                requests,
                lambda html: html.json().get('result', [])
            )
            for obj in sublist
        ]
        # calculate average of listings
        avg_rate = 0
        num_results = 0
        for return_obj in return_objs:
            if 'item' in return_obj and 'exchange' in return_obj:
                exchange_rate = return_obj['item']['amount'] / return_obj['exchange']['amount']
                avg_rate += exchange_rate
                num_results += 1
        if num_results == 0:
            return None
        avg_rate /= num_results
        return avg_rate

    def fetch_exchange_rate_poe_ninja(self, have, want):
        exchange_rates = self.poe_ninja_client.get_currency_data()
        for name, value in exchange_rates.items():
            try:
                self.exchange_rates[CURRENCIES[name]]['chaos'] = value
            except KeyError:  # currency returned by poe ninja is not a recognized currency
                pass
        have_to_want = self.exchange_rates[have]['chaos'] / self.exchange_rates[want]['chaos']
        return have_to_want
