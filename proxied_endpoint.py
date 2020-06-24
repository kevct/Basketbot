import asyncio
import random
from time import time
from typing import Set
import logging

from proxybroker import Broker
from requests.exceptions import ReadTimeout, ProxyError, SSLError, ConnectTimeout, ConnectionError
from nba_api.stats.endpoints.commonplayerinfo import CommonPlayerInfo

GOOD_PROXIES = set()
BAD_PROXIES = set()
BLOCKED_PROXIES = set()
DIRECT_CONNECT_ALLOWED = None
GOOD_PROXIES_DEFAULTFILE = 'good_proxies.txt'
BAD_PROXIES_DEFAULTFILE = 'bad_proxies.txt'
BLOCKED_PROXIES_DEFAULTFILE = 'blocked_proxies.txt'
LOGGER = logging.getLogger(__name__)


def load_proxies_from_file(good_proxies_filename: str = None,
                           bad_proxies_filename: str = None,
                           blocked_proxies_filename: str = None):
    file_errors = []
    if good_proxies_filename is not None:
        try:
            with open(good_proxies_filename, 'r') as f:
                num_loaded = 0
                for line in f:
                    GOOD_PROXIES.add(line.strip())
                    num_loaded += 1
                LOGGER.debug(f"Loaded {num_loaded} good proxies from {good_proxies_filename}")
        except FileNotFoundError as e:
            file_errors.append(e)

    if bad_proxies_filename is not None:
        try:
            with open(bad_proxies_filename, 'r') as f:
                num_loaded = 0
                for line in f:
                    BAD_PROXIES.add(line.strip())
                    num_loaded += 1
                LOGGER.debug(f"Loaded {num_loaded} bad proxies from {bad_proxies_filename}")
        except FileNotFoundError as e:
            file_errors.append(e)

    if blocked_proxies_filename is not None:
        try:
            with open(blocked_proxies_filename, 'r') as f:
                num_loaded = 0
                for line in f:
                    BLOCKED_PROXIES.add(line.strip())
                    num_loaded += 1
                LOGGER.debug(f"Loaded {num_loaded} blocked proxies from {bad_proxies_filename}")
        except FileNotFoundError as e:
            file_errors.append(e)

    if len(file_errors) > 0:
        raise FileNotFoundError(file_errors)


def save_proxies_to_file(good_proxies_filename: str = None,
                         bad_proxies_filename: str = None,
                         blocked_proxies_filename: str = None):
    with open(good_proxies_filename, 'w') as f:
        for proxy_url in GOOD_PROXIES:
            f.write(proxy_url + '\n')
    with open(bad_proxies_filename, 'w') as f:
        for proxy_url in BAD_PROXIES:
            f.write(proxy_url + '\n')
    with open(blocked_proxies_filename, 'w') as f:
        for proxy_url in BLOCKED_PROXIES:
            f.write(proxy_url + '\n')


async def process_grabbed_proxies(grabbed_proxies: asyncio.Queue, proxies_to_test: Set[str], min_proxies=10, timeout=5):
    while len(proxies_to_test) < min_proxies:

        try:
            proxy = await asyncio.wait_for(grabbed_proxies.get(), timeout=timeout)
        except asyncio.TimeoutError:
            LOGGER.debug("ProxyBroker queue timing out")
            break

        if proxy is not None:
            proxy_url = f"{proxy.host}:{proxy.port}"
            LOGGER.debug(f"Got {proxy_url}")
            if proxy_url not in GOOD_PROXIES and \
                    proxy_url not in BAD_PROXIES and \
                    proxy_url not in BLOCKED_PROXIES:
                proxies_to_test.add(proxy_url)


async def populate_good_proxies(good_proxies_filename: str = GOOD_PROXIES_DEFAULTFILE,
                          bad_proxies_filename: str = BAD_PROXIES_DEFAULTFILE,
                          blocked_proxies_filename: str = BLOCKED_PROXIES_DEFAULTFILE,
                          min_good_proxies: int = 1,
                          load_from_file: bool = False,
                          save_to_file=True,
                          broker_timeout: int = 5,
                          proxy_test_batch_size: int = 10,
                          player_id_to_test=2544):
    if load_from_file:
        try:
            load_proxies_from_file(good_proxies_filename, bad_proxies_filename, blocked_proxies_filename)
        except FileNotFoundError:
            pass

    proxies_to_test = set()
    grabbed_proxies = asyncio.Queue()
    broker = Broker(grabbed_proxies, timeout=broker_timeout)

    while len(GOOD_PROXIES) < min_good_proxies:
        proxy_processor = process_grabbed_proxies(grabbed_proxies, proxies_to_test,
                                                       min_proxies=proxy_test_batch_size)
        tasks = await asyncio.gather(broker.grab(countries=['US']),
                               proxy_processor)

        try:
            LOGGER.debug("Starting proxy finding async loop")
            await proxy_processor
        except OSError:
            LOGGER.debug("ProxyBroker OSError caught")
            # Needed due to bug in ProxyBroker (https://github.com/constverum/ProxyBroker/issues/130)
            pass
        except RuntimeError:
            LOGGER.debug("ProxyBroker RuntimeError caught")
            # Needed due to bug in ProxyBroker (https://github.com/constverum/ProxyBroker/issues/25)
            pass

        # If ProxyBroker runs out of URLs, reset it and empty the bad proxies list
        # Bad proxies just failed when they originally were tested, so they might work now
        # It's unlikely that blocked proxies will ever be unblocked, so keep that list
        if len(proxies_to_test) < 1:
            LOGGER.debug("Clearing bad proxy list and resetting ProxyBroker")
            broker = Broker(grabbed_proxies, timeout=broker_timeout)
            BAD_PROXIES.clear()

        else:
            LOGGER.debug(f"testing {len(proxies_to_test)} proxies")

            #Lock the set so we can access it safely
            for proxy_url in list(proxies_to_test):

                try:
                    start = time()
                    CommonPlayerInfo(player_id=player_id_to_test, proxy=proxy_url, timeout=5).get_normalized_dict()
                    end = time()
                    LOGGER.debug(f"proxy connection from {proxy_url} succeeded in {round(end - start, 4)} seconds")
                    GOOD_PROXIES.add(proxy_url)

                except ReadTimeout:
                    # We don't know 100% that the proxy is actually blocked,
                    # but this is pretty much the only indication we have
                    LOGGER.debug("stats.nba.com timed out (Probably blocked)")
                    BLOCKED_PROXIES.add(proxy_url)

                except (ProxyError, ConnectTimeout, SSLError, ConnectionError) as e:
                    LOGGER.debug(f"proxy connection from {proxy_url} failed with error {e}")
                    BAD_PROXIES.add(proxy_url)

                # Give control back to the main event loop so we can still hit the heartbeat
                await asyncio.sleep(0)

                if save_to_file:
                    save_proxies_to_file(good_proxies_filename, bad_proxies_filename, blocked_proxies_filename)

    return


async def get_random_good_proxy() -> str:
        while True:
            try:
                return random.choice(tuple(GOOD_PROXIES))
            except IndexError:
                LOGGER.debug("Tried to get a good proxy but there were none.")

                # lock the good proxies list so we don't get race conditions
                # with multiple calls trying to populate the proxy list
                await populate_good_proxies()
                pass


# Code copied from https://github.com/swar/nba_api/blob/master/tests/stats/deferred_endpoints.py
class DeferredEndpoint:
    # Simple class to represent an endpoint with deferred evaluation.

    def __init__(self, endpoint_class, **kwargs):
        self.endpoint_class = endpoint_class
        self.kwargs = kwargs

    def __call__(self):
        return self.endpoint_class(**self.kwargs)


def ProxiedEndpoint(endpoint_class, **kwargs):
    # Modified version of DeferredEndpoint to automatically get the current proxy and use it

        if (kwargs.get('use_proxy') is None and not is_direct_connect_allowed()) or \
            (kwargs.get('use_proxy') is not None and kwargs['use_proxy']):

            # If the use_proxy argument was specified, remove it
            kwargs.pop('use_proxy', None)

            while True:
                proxy_url = asyncio.run(get_random_good_proxy())

                # insert the proxy url into the arguments for the endpoint call
                kwargs['proxy'] = proxy_url

                try:
                    # try to access the endpoint
                    return endpoint_class(**kwargs)

                except (ReadTimeout, ProxyError, ConnectTimeout, SSLError, ConnectionError) as e:
                    LOGGER.debug(f"Previously good proxy {proxy_url} failed with error {e}")
                    GOOD_PROXIES.remove(proxy_url)

        else:
            LOGGER.debug("Directly calling endpoint")
            # If the use_proxy argument was specified, remove it
            kwargs.pop('use_proxy', None)
            return endpoint_class(**kwargs)


def clear_all_proxy_lists():
    GOOD_PROXIES.clear()
    BAD_PROXIES.clear()
    BLOCKED_PROXIES.clear()


def test_nba_noproxy() -> bool:
    '''
    Test to see if a proxy is even needed
    :return:
    '''
    global DIRECT_CONNECT_ALLOWED

    LOGGER.debug("Calling the NBA API to see if it responds")
    try:
        CommonPlayerInfo(player_id=2544).get_response()
    except ReadTimeout:
        LOGGER.debug("Direct connection to NBA timed out")
        DIRECT_CONNECT_ALLOWED = False
        return False

    LOGGER.debug("Direct connection to NBA succeeded")
    DIRECT_CONNECT_ALLOWED = True
    return True


def is_direct_connect_allowed() -> bool:
    global DIRECT_CONNECT_ALLOWED

    while DIRECT_CONNECT_ALLOWED is None:
        test_nba_noproxy()

    return DIRECT_CONNECT_ALLOWED
