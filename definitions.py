from os.path import dirname, abspath, join, exists
from os import makedirs

# Root backend directory
# join used here to eliminate problems with different filesystem formats
ROOT_DIR = dirname(abspath(__file__))
CONF_PATH = join(ROOT_DIR, "conf/")
LOG_PATH = join(ROOT_DIR, "log/")

TOKEN_FILE = join(CONF_PATH, "token.txt")
GOOD_PROXIES_FILE = join(CONF_PATH, 'good_proxies.txt')
BAD_PROXIES_FILE = join(CONF_PATH, 'bad_proxies.txt')
BLOCKED_PROXIES_FILE = join(CONF_PATH, 'blocked_proxies.txt')

# Ensure the conf and log folders exist
if not exists(CONF_PATH):
    makedirs(CONF_PATH)

if not exists(LOG_PATH):
    makedirs(LOG_PATH)