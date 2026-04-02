from urllib.parse import urlparse

from .base import BaseSite
from .freewebnovel import FreeWebNovel
from .fanmtl import FanMTL
from .wuxiabox import WuxiaBox

_SITE_MAP: dict[str, type[BaseSite]] = {
    "freewebnovel.com": FreeWebNovel,
    "fanmtl.com": FanMTL,
    "wuxiabox.com": WuxiaBox,
}

SUPPORTED_SITES = list(_SITE_MAP.keys())


def site_for_url(url: str) -> BaseSite | None:
    host = urlparse(url).netloc.lstrip("www.")
    for domain, cls in _SITE_MAP.items():
        if domain in host:
            return cls()
    return None
