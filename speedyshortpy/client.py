"""
Client wrapper for the SpeedyShort URL shortener API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class ShortLink:
    """Represents a short link created by SpeedyShort."""

    code: str
    short_url: str
    target_url: str


class SpeedyShortClient:
    """
    Simple client for the SpeedyShort HTTP API.

    By default it targets a local instance running on http://localhost:8080,
    but you can point it to any reachable SpeedyShort installation, for example:

        client = SpeedyShortClient(base_url="https://syrt.cc")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    @property
    def session(self) -> requests.Session:
        return self._session

    def shorten(self, url: str) -> ShortLink:
        """
        Create a short link for the given URL.

        :param url: The original long URL.
        :return: ShortLink with code, short URL and target URL.
        :raises requests.HTTPError: if the API returns an error.
        """
        endpoint = f"{self.base_url}/api/shorten"
        resp = self._session.post(
            endpoint,
            json={"url": url},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return ShortLink(
            code=data["code"],
            short_url=data["short_url"],
            target_url=data["target_url"],
        )

    def resolve(self, code: str, follow_redirects: bool = False) -> requests.Response:
        """
        Perform a GET request for the given short code.

        This is mostly useful if you want to inspect the redirect response.
        If follow_redirects is False, the Response will usually have status_code 301/302
        and the target URL in the 'Location' header.

        :param code: Short code (e.g. 'a7X9pQ').
        :param follow_redirects: Whether to follow redirects automatically.
        :return: requests.Response
        """
        url = f"{self.base_url}/{code.lstrip('/')}"
        resp = self._session.get(url, timeout=self.timeout, allow_redirects=follow_redirects)
        return resp
