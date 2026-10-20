from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urlsplit

from app.config import allowed_test_origins


class UnsafeTarget(ValueError):
    pass


def origin_of(url: str) -> str:
    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if not scheme or not host:
        raise UnsafeTarget("A complete HTTP(S) URL is required.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise UnsafeTarget("The URL contains an invalid port.") from exc
    if port == 0:
        raise UnsafeTarget("Port 0 is not a valid scan destination.")
    default_port = 443 if scheme == "https" else 80
    display_host = f"[{host}]" if ":" in host else host
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{scheme}://{display_host}{suffix}"


def validate_http_url(url: str) -> str:
    """Validate a navigation target and reject credentials/non-HTTP schemes."""
    if any(ord(char) < 32 for char in url) or any(char.isspace() for char in url):
        raise UnsafeTarget("The URL must not contain whitespace or control characters.")
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeTarget("Only HTTP and HTTPS URLs can be scanned.")
    if not parsed.hostname:
        raise UnsafeTarget("A hostname is required.")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeTarget("URLs containing a username or password are not allowed.")
    origin = origin_of(url)
    authorize_network_url(url)
    return origin


def authorize_network_url(url: str) -> None:
    """Block non-public destinations unless their exact origin is configured."""
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeTarget("Only HTTP and HTTPS network requests are allowed.")
    origin = origin_of(url)
    app_origin = os.environ.get("SCANNER_UI_ORIGIN", "http://127.0.0.1:8765").rstrip("/")
    if origin == app_origin:
        raise UnsafeTarget("The local scanner control UI cannot be scanned as a target.")
    if origin in allowed_test_origins():
        return

    host = parsed.hostname or ""
    try:
        literal = ipaddress.ip_address(host)
        addresses = {literal}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(item[4][0].split("%", 1)[0])
                for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80))
            }
        except (OSError, ValueError) as exc:
            raise UnsafeTarget("The hostname could not be resolved safely.") from exc

    if not addresses or any(not address.is_global for address in addresses):
        raise UnsafeTarget("Private, local, and non-global network addresses are blocked by default.")
