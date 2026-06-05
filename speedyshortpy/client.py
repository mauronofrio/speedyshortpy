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

        If follow_redirects is False, the response will usually have status 301/302
        and the target URL in the 'Location' header.
        If the link has been blocked, the response will have status 451.

        :param code: Short code (e.g. 'a7X9pQ').
        :param follow_redirects: Whether to follow redirects automatically.
        :return: requests.Response
        """
        url = f"{self.base_url}/{code.lstrip('/')}"
        resp = self._session.get(url, timeout=self.timeout, allow_redirects=follow_redirects)
        return resp

    def report(self, url: str, reason: str) -> None:
        """
        Submit an abuse report for a short link.

        The url parameter accepts any of the following formats:
          - short code only:       'a7X9pQ'
          - full short URL:        'https://syrt.cc/a7X9pQ'
          - full external URL:     'https://malicious.com/page'

        The server resolves the domain to act on regardless of the format.

        :param url: The short link or URL to report.
        :param reason: A description of why the link is being reported (10–100 characters).
        :raises ValueError: if reason length is not between 10 and 100 characters.
        :raises requests.HTTPError: if the API returns an error.
        """
        reason = reason.strip()
        if not 10 <= len(reason) <= 100:
            raise ValueError(f"reason must be between 10 and 100 characters (got {len(reason)})")

        endpoint = f"{self.base_url}/api/report"
        resp = self._session.post(
            endpoint,
            json={"code": url, "reason": reason},
            timeout=self.timeout,
        )
        resp.raise_for_status()
