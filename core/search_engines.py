"""Dark Web Meta-Search Engine using Async HTTP targeting popular Onion indexes.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from aiohttp_socks import ProxyConnector
except ImportError:
    ProxyConnector = None

from config import USER_AGENT, REQUEST_TIMEOUT, TOR_PROXY
from utils.logger import get_logger

LOGGER = get_logger(__name__)


# DeepWeb Search Engines curated for intelligence gathering
SEARCH_ENGINES = [
    {"name": "Ahmia", "url": "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}"},
    {"name": "OnionLand", "url": "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search?q={query}"},
    {"name": "Torgle", "url": "http://iy3544gmoeclh5de6gez2256v6pjh4omhpqdh2wpeeppjtvqmjhkfwad.onion/torgle/?query={query}"},
    {"name": "Kaizer", "url": "http://kaizerwfvp5gxu6cppibp7jhcqptavq3iqef66wbxenh6a2fklibdvid.onion/search?q={query}"},
    {"name": "Amnesia", "url": "http://amnesia7u5odx5xbwtpnqk3edybgud5bmiagu75bnqx2crntw5kry7ad.onion/search?query={query}"},
    {"name": "Anima", "url": "http://anima4ffe27xmakwnseih3ic2y7y3l6e7fucwk4oerdn4odf7k74tbid.onion/search?q={query}"},
    {"name": "Find Tor", "url": "http://findtorroveq5wdnipkaojfpqulxnkhblymc7aramjzajcvpptd4rjqd.onion/search?q={query}"},
    {"name": "TorNet", "url": "http://tornetupfu7gcgidt33ftnungxzyfq2pygui5qdoyss34xbgx2qruzid.onion/search?q={query}"},
    {"name": "Onionway", "url": "http://oniwayzz74cv2puhsgx4dpjwieww4wdphsydqvf5q7eyz4myjvyw26ad.onion/search.php?s={query}"},
    {"name": "Torgol", "url": "http://torgolnpeouim56dykfob6jh5r2ps2j73enc42s2um4ufob3ny4fcdyd.onion/?q={query}"},
    {"name": "OSS", "url": "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion/oss/index.php?search={query}"},
]


class AsyncMetaSearch:
    """Async metasearch across multiple dark web search engines."""

    def __init__(self, proxy_url: str = TOR_PROXY):
        self.proxy_url = proxy_url
        self.headers = {"User-Agent": USER_AGENT}

    async def fetch_results(self, session: aiohttp.ClientSession, engine: dict[str, str], query: str) -> list[dict[str, str]]:
        if aiohttp is None:
            return []
        url = engine["url"].format(query=query)
        links = []
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                if response.status == 200:
                    html = await response.text()
                    # Generic regex to rip onion URLs from search engines
                    raw_urls = re.findall(r'https?:\/\/[a-z0-9\.]+\.onion[^\s"\'<]*', html)
                    for raw in raw_urls:
                        if "search" not in raw and "onionland" not in raw:
                            links.append({"engine": engine["name"], "url": raw})
                    LOGGER.debug(f"[{engine['name']}] Found {len(links)} links for '{query}'.")
        except Exception as e:
            LOGGER.debug(f"[{engine['name']}] Search failed: {e}")
            
        return links

    async def search(self, query: str) -> list[dict[str, str]]:
        """Asynchronously perform a meta-search and deduplicate results."""
        if aiohttp is None:
            LOGGER.warning("aiohttp is not installed; async meta-search is unavailable")
            return []

        LOGGER.info(f"Initiating meta-search across {len(SEARCH_ENGINES)} search engines for '{query}'...")
        
        proxy = self.proxy_url.replace("socks5h://", "socks5://") if self.proxy_url else None
        connector = ProxyConnector.from_url(proxy) if (proxy and ProxyConnector is not None) else None
        
        results = []
        async with aiohttp.ClientSession(connector=connector, headers=self.headers) as session:
            tasks = [self.fetch_results(session, engine, query) for engine in SEARCH_ENGINES]
            all_responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in all_responses:
                if isinstance(res, list):
                    results.extend(res)
                    
        # Deduplication mapping URL to engines that found them
        deduped: dict[str, list[str]] = {}
        for r in results:
            url = r["url"].rstrip("/")
            if url not in deduped:
                deduped[url] = []
            deduped[url].append(r["engine"])
            
        final_results = [{"url": k, "found_by": sorted(list(set(v)))} for k, v in deduped.items()]
        LOGGER.info(f"Meta-search completed. {len(final_results)} unique onion services found.")
        return final_results
