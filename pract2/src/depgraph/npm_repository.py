"""Repository backed by an npm registry that is accessed over HTTP.

Only the standard library is used. The manifest of the latest version of
a package is requested directly from the registry
(``GET <registry>/<package>/latest``) and its ``dependencies`` field is
read.
"""

import http.client
import json
import urllib.error
import urllib.request
from http import HTTPStatus
from urllib.parse import quote

from depgraph.errors import PackageNotFoundError, RepositoryError

TIMEOUT_SECONDS = 15
LATEST_TAG = "latest"
USER_AGENT = "depgraph/1.0"


def _http_error(error, name):
    """Convert an HTTP error into a repository error."""
    if error.code == HTTPStatus.NOT_FOUND:
        return PackageNotFoundError(
            f"package {name!r} not found in the repository"
        )
    return RepositoryError(f"repository answered HTTP {error.code}")


def _decode_manifest(body, url):
    """Parse the JSON body of the registry answer."""
    try:
        manifest = json.loads(body)
    except ValueError as error:
        raise RepositoryError(f"invalid JSON received from {url}") from error
    if not isinstance(manifest, dict):
        raise RepositoryError(f"unexpected answer received from {url}")
    return manifest


def fetch_manifest(url, name):
    """Download and decode the package manifest located at the URL."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as reply:
            body = reply.read()
    except urllib.error.HTTPError as error:
        raise _http_error(error, name) from error
    except (OSError, ValueError, http.client.HTTPException) as error:
        raise RepositoryError(f"cannot connect to {url}: {error}") from error
    return _decode_manifest(body, url)


class NpmRepository:
    """Direct dependencies of npm packages taken from a registry."""

    def __init__(self, base_url):
        """Remember the registry URL; answers are cached per package."""
        self._base_url = base_url.rstrip("/")
        self._cache = {}

    def dependencies(self, name):
        """Return the names of the direct dependencies of a package."""
        if name not in self._cache:
            self._cache[name] = self._load(name)
        return list(self._cache[name])

    def packages(self):
        """The registry cannot list all packages, so this always fails."""
        raise RepositoryError(
            "the list of all packages is not available in an npm registry"
        )

    def _load(self, name):
        """Request the latest manifest of the package."""
        url = f"{self._base_url}/{quote(name, safe='@')}/{LATEST_TAG}"
        manifest = fetch_manifest(url, name)
        dependencies = manifest.get("dependencies", {})
        if not isinstance(dependencies, dict):
            raise RepositoryError(
                f"invalid 'dependencies' field of package {name!r}"
            )
        return list(dependencies)
