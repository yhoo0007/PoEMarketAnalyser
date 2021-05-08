import requests
import time

from .rate import Rate


class RequestClient:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def get_request_interval(self, rate_limits, num_requests):
        rate_limits = [
            Rate(int(num_requests), int(interval), int(timeout))
        for num_requests, interval, timeout in map(lambda e: e.split(':'), rate_limits)]

        best_rate = max(rate_limits, key=lambda rate: rate.interval)
        for rate in rate_limits:
            if rate.num_requests >= num_requests and rate.interval < best_rate.interval:
                best_rate = rate
        return round(best_rate.interval / best_rate.num_requests, 2) + 0.05

    def post(self, *args, **kwargs):
        while True:
            html = requests.post(*args, **kwargs)
            if html.status_code == 429:
                retry_after = int(html.headers['Retry-After'])
                print('429: Retying after:', retry_after)
                time.sleep(retry_after)
                continue
            return html

    def get(self, *args, **kwargs):
        while True:
            html = requests.get(*args, **kwargs)
            if html.status_code == 429:
                retry_after = int(html.headers['Retry-After'])
                print('429: Retying after:', retry_after)
                time.sleep(retry_after)
                continue
            return html

    def _request_map(self, method, reqs, function):
        request_interval = None
        ret = []
        for i, request in enumerate(reqs, 1):
            html = method(request['url'], **request['kwargs'])
            if request_interval is None:
                rate_limits = html.headers['X-Rate-Limit-Ip'].split(',')
                request_interval = self.get_request_interval(rate_limits, len(reqs))
            if self.verbose:
                print(f'\r{i}/{len(reqs)}', end='')
            ret.append(function(html))
            time.sleep(request_interval)
        if self.verbose:
            print()
        return ret

    def post_map(self, reqs, function):
        return self._request_map(self.post, reqs, function)

    def get_map(self, reqs, function):
        return self._request_map(self.get, reqs, function)

if __name__ == '__main__':
    from config import LEAGUE, POESESSID

    url = f'https://www.pathofexile.com/api/trade/exchange/{LEAGUE}'
    query = {
        'exchange': {
            'status': {'option': 'online'},
            'have': ['chaos'],
            'want': ['alt']
        }
    }
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36'
    }
    cookies = {'cookie': POESESSID}
    request_client = RequestClient()
    # html = request_client.post(url, json=query, headers=headers, cookies=cookies)
    # print(html)

    request = {
        'url': url,
        'kwargs': {
            'json': query,
            'headers': headers,
            'cookies': cookies
        },
    }
    ret = request_client.post_map([request] * 35, lambda html: html.json())
    print(ret)
