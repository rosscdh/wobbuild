import logging

from djehouty.libgelf.handlers import GELFTCPSocketHandler

logger = logging.getLogger('wobbuild')
logger.setLevel(logging.DEBUG)

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
