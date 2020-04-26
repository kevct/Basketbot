from typing import Set

import functions
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo
import asyncio
from proxybroker import Broker
from requests.exceptions import ReadTimeout, ProxyError, SSLError, ConnectTimeout, ConnectionError
from time import time

async def fill_proxy_list(proxies: asyncio.Queue, proxy_list: Set[str], bad_proxies: Set[str], min_proxies: int = 10):

    while len(proxies_list) < min_proxies:
        filtered = 0
        added = 0

        try:
            proxy = await asyncio.wait_for(proxies.get(), timeout=30)
        except asyncio.TimeoutError:
            break

        if proxy is not None and f"{proxy.host}:{proxy.port}" not in good_proxies and f"{proxy.host}:{proxy.port}" not in bad_proxies and f"{proxy.host}:{proxy.port}" not in blocked_proxies:
            proxy_list.add(f"{proxy.host}:{proxy.port}")
            print('Proxy found')
        else:
            print(f'{proxy} filtered')

good_proxies = set()
bad_proxies = set()
blocked_proxies = set()

try:
    with open('log/good_proxies.txt', 'r') as f:
        for line in f:
            good_proxies.add(line.strip())
except FileNotFoundError:
    pass
print(f"Read {len(good_proxies)} good proxies from file")

try:
    with open('log/bad_proxies.txt', 'r') as f:
        for line in f:
            bad_proxies.add(line.strip())
except FileNotFoundError:
    pass
print(f"Read {len(bad_proxies)} bad proxies from file")

try:
    with open('log/blocked_proxies.txt', 'r') as f:
        for line in f:
            blocked_proxies.add(line.strip())
except FileNotFoundError:
    pass
print(f"Read {len(blocked_proxies)} blocked proxies from file")

name = 'Lebron James'
dict = functions.getPlayerIdsByName(name)
id = list(dict.keys())[0]
print(f"Player id: {list(dict.keys())[0]}")

proxies = asyncio.Queue()
broker = Broker(proxies, timeout=5)

while(True):
#while len(tested_proxies) <= 0:
    proxies_list = set()

    tasks = asyncio.gather(broker.grab(countries=['US']), fill_proxy_list(proxies, proxies_list, bad_proxies))
    loop = asyncio.get_event_loop()
    print('Finding proxies')


    try:
        loop.run_until_complete(tasks)

    except asyncio.TimeoutError:
        # Needed due to bug in ProxyBroker (https://github.com/constverum/ProxyBroker/issues/127)
        pass
    except OSError:
        # Needed due to bug in ProxyBroker (https://github.com/constverum/ProxyBroker/issues/130)
        pass
    except RuntimeError:
        # Needed due to bug in ProxyBroker (https://github.com/constverum/ProxyBroker/issues/25)
        pass

    # When the broker breaks, it starts completing immediately. Reinstantiate it if that happens
    if len(proxies_list) < 1:
        print('Resetting ProxyBroker')
        broker = Broker(proxies, timeout=3)

    else:
        for proxy in proxies_list:
            print(f"Running request from {proxy}: ", end='')
            try:
                start = time()
                CommonPlayerInfo(player_id=id, proxy=proxy, timeout=5).get_normalized_dict()
                end = time()
                good_proxies.add(proxy)
                print(f"Success ({round(end-start, 4)} s)")

            except ReadTimeout:
                # We don't know 100% that the proxy is actually blocked, but this is pretty much the only indication we have
                blocked_proxies.add(proxy)
                print("stats.nba.com timed out (Proxy Blocked)")

            except ProxyError:
                bad_proxies.add(proxy)
                print("Proxy Error")

            except ConnectTimeout:
                bad_proxies.add(proxy)
                print("Proxy timed out")

            except SSLError:
                bad_proxies.add(proxy)
                print("SSL Error")

            except ConnectionError:
                '''
                So, this one doesn't come up a lot. When it did, this was the message:
                evrimiçi kullanicilarin sayisi lisansin iznini asiyor. Lisansinizi yükseltmeniz
                ya da satin almaniz gerekir.
                According to Google Translate, this is Turkish and means:
                The number of online users is permitting the license. You must upgrade or purchase your license.
                Obviously someone uploaded a paid proxy server to one of the lists.
                '''
                bad_proxies.add(proxy)
                print("Connection Error")

        print(f"{len(good_proxies)} good proxies")
        print(f"{len(bad_proxies)} bad proxies")
        print(f"{len(blocked_proxies)} blocked proxies")
        with open("log/blocked_proxies.txt", 'w') as f:
            for proxy_url in blocked_proxies:
                f.write(proxy_url + '\n')
        with open("log/good_proxies.txt", 'w') as f:
            for proxy_url in good_proxies:
                f.write(proxy_url + '\n')
        with open("log/bad_proxies.txt", 'w') as f:
            for proxy_url in bad_proxies:
                f.write(proxy_url + '\n')