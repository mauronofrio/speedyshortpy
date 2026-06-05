# speedyshortpy

`speedyshortpy` is a small Python client for the [SpeedyShort](https://github.com/mauronofrio/SpeedyShort)
URL shortener.

It provides a thin wrapper around the HTTP API so you can create short links from Python
code with a single call.

## Installation

Once published on PyPI:

```bash
pip install speedyshortpy
```

For local development, you can install it from the cloned repository:

```bash
pip install -e .
```

## Usage

By default the client targets a local SpeedyShort instance on `http://localhost:8080`:

```python
from speedyshortpy import SpeedyShortClient

client = SpeedyShortClient()  # base_url="http://localhost:8080"

result = client.shorten("https://www.example.com")
print(result.code)
print(result.short_url)
print(result.target_url)
```

You can also point it to a remote instance, for example the public demo:

```python
client = SpeedyShortClient(base_url="https://syrt.cc")
```

### Resolving a short code

You usually do not need a client for redirects, but if you want to inspect
the redirect response:

```python
resp = client.resolve("a7X9pQ", follow_redirects=False)
print(resp.status_code)          # 301 if active, 451 if blocked
print(resp.headers.get("Location"))
```

A blocked link returns HTTP **451** instead of a redirect.

### Reporting a link

You can report a short link for abuse. The `url` parameter accepts a short
code, a full short URL, or a full external URL — the server resolves the
domain automatically.

```python
# Using just the short code
client.report("a7X9pQ", reason="This link points to a phishing page")

# Using the full short URL
client.report("https://syrt.cc/a7X9pQ", reason="This link points to a phishing page")

# Using a full external URL
client.report("https://malicious.com/page", reason="Malware distribution site")
```

The `reason` must be between **10 and 100 characters**. A `ValueError` is raised
client-side if the constraint is not met. The report is queued for manual review
and does not immediately block the link.

Rate limit: **3 reports per IP per day**.

## License

This client library is released under the same license as the main project:
**Prosperity Public License 3.0.0**.

Commercial use requires a commercial license from the copyright holder.
