from __future__ import annotations

import socket
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WILDCARD_HOSTS = {"0.0.0.0", "::"}


def format_row_one_site_url(host: str, port: int) -> str:
    return f"http://{_format_url_host(_browser_host_for_bind(host))}:{port}"


def format_row_one_site_access_message(host: str, port: int) -> str:
    local_url = format_row_one_site_url(host, port)
    if host in WILDCARD_HOSTS:
        return "\n".join(
            (
                f"Open locally: {local_url}",
                f"Open from LAN: http://<LAN-IP>:{port}",
                f"Bound to {host}:{port}. The ROW ONE local server has no authentication.",
            )
        )
    return f"Open: {local_url}"


def create_row_one_http_server(
    *,
    site_dir: Path,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    _validate_site_dir(site_dir)
    handler = partial(SimpleHTTPRequestHandler, directory=str(site_dir))
    server_class = _http_server_class(host)
    return server_class((host, port), handler)


def serve_row_one_site(
    *,
    site_dir: Path,
    host: str,
    port: int,
) -> None:
    server = create_row_one_http_server(site_dir=site_dir, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def _validate_site_dir(site_dir: Path) -> None:
    marker_path = site_dir / ".row-one-site"
    if not marker_path.exists():
        raise FileNotFoundError(f"ROW ONE site marker not found at {marker_path}")
    index_path = site_dir / "index.html"
    if not index_path.exists():
        raise FileNotFoundError(f"ROW ONE site index.html not found at {index_path}")


def _browser_host_for_bind(host: str) -> str:
    if host == "0.0.0.0":
        return "127.0.0.1"
    if host == "::":
        return "::1"
    return host


def _format_url_host(host: str) -> str:
    if ":" in host and not host.startswith("["):
        return f"[{host}]"
    return host


def _http_server_class(host: str) -> type[ThreadingHTTPServer]:
    if ":" not in host:
        return ThreadingHTTPServer

    class RowOneIPv6HTTPServer(ThreadingHTTPServer):
        address_family = socket.AF_INET6

    return RowOneIPv6HTTPServer
