import logging

from djehouty.libgelf.handlers import GELFTCPSocketHandler
from pip.utils.logging import BetterRotatingFileHandler

logger = logging.getLogger('wobbuild')
logger.setLevel(logging.DEBUG)

rotating_handler = BetterRotatingFileHandler('wobbuild.log')

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

logger.addHandler(gelf_handler)
logger.addHandler(rotating_handler)
