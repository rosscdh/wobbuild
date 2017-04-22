import logging

from djehouty.libgelf.handlers import GELFTCPSocketHandler
from pip.utils.logging import BetterRotatingFileHandler
formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s:%(lineno)d %(msg)s')
logging.basicConfig(datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger('wobbuild')
logger.setLevel(logging.DEBUG)

rotating_handler = BetterRotatingFileHandler('wobbuild.log')
rotating_handler.setFormatter(formatter)

gelf_handler = GELFTCPSocketHandler(
    host='127.0.0.1',
    port=5140,
    static_fields={
        'app': 'wobbuild',
        'env': 'development',
    },
    use_tls=True,
    level=logging.DEBUG,
    null_character=True,
)
gelf_handler.setFormatter(formatter)

logger.addHandler(gelf_handler)
logger.addHandler(rotating_handler)
