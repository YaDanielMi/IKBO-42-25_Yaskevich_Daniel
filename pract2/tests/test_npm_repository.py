"""Tests for the npm registry repository (the network is mocked)."""

import json
import unittest
import urllib.error
from unittest import mock

from depgraph.errors import PackageNotFoundError, RepositoryError
from depgraph.npm_repository import NpmRepository

URLOPEN = "depgraph.npm_repository.urllib.request.urlopen"
BASE_URL = "https://registry.example.org/"


class FakeReply:
    """Minimal stand-in for the object returned by urlopen."""

    def __init__(self, body):
        """Keep the raw body that read() will return."""
        self._body = body

    def read(self):
        """Return the body."""
        return self._body

    def __enter__(self):
        """Support the with statement."""
        return self

    def __exit__(self, *exc_info):
        """Do not swallow exceptions."""
        return False


def manifest_reply(manifest):
    """Create a fake reply with a JSON encoded manifest."""
    return FakeReply(json.dumps(manifest).encode("utf-8"))


class NpmRepositoryTests(unittest.TestCase):
    """Reading dependencies from a registry."""

    def test_reads_direct_dependencies(self):
        """Names of the 'dependencies' field are returned in order."""
        manifest = {"name": "p", "dependencies": {"b": "^1", "a": "~2"}}
        with mock.patch(URLOPEN, return_value=manifest_reply(manifest)):
            result = NpmRepository(BASE_URL).dependencies("p")
        self.assertEqual(result, ["b", "a"])

    def test_missing_dependencies_field(self):
        """A package without dependencies gives an empty list."""
        with mock.patch(URLOPEN, return_value=manifest_reply({"name": "p"})):
            self.assertEqual(NpmRepository(BASE_URL).dependencies("p"), [])

    def test_request_url_of_scoped_package(self):
        """The scope slash is escaped and the latest tag is requested."""
        with mock.patch(URLOPEN, return_value=manifest_reply({})) as urlopen:
            NpmRepository(BASE_URL).dependencies("@types/node")
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://registry.example.org/@types%2Fnode/latest",
        )

    def test_answers_are_cached(self):
        """Each package is requested only once."""
        with mock.patch(URLOPEN, return_value=manifest_reply({})) as urlopen:
            repository = NpmRepository(BASE_URL)
            repository.dependencies("p")
            repository.dependencies("p")
        self.assertEqual(urlopen.call_count, 1)

    def test_not_found(self):
        """HTTP 404 means that the package does not exist."""
        error = urllib.error.HTTPError(BASE_URL, 404, "Not Found", {}, None)
        with mock.patch(URLOPEN, side_effect=error):
            with self.assertRaises(PackageNotFoundError):
                NpmRepository(BASE_URL).dependencies("p")

    def test_other_http_error(self):
        """Other HTTP errors are repository errors."""
        error = urllib.error.HTTPError(BASE_URL, 500, "Oops", {}, None)
        with mock.patch(URLOPEN, side_effect=error):
            with self.assertRaises(RepositoryError):
                NpmRepository(BASE_URL).dependencies("p")

    def test_connection_error(self):
        """Network failures are repository errors."""
        error = urllib.error.URLError("no route to host")
        with mock.patch(URLOPEN, side_effect=error):
            with self.assertRaises(RepositoryError):
                NpmRepository(BASE_URL).dependencies("p")

    def test_invalid_json(self):
        """A body that is not JSON is a repository error."""
        with mock.patch(URLOPEN, return_value=FakeReply(b"<html>")):
            with self.assertRaises(RepositoryError):
                NpmRepository(BASE_URL).dependencies("p")

    def test_invalid_dependencies_field(self):
        """The 'dependencies' field must be an object."""
        reply = manifest_reply({"dependencies": ["a"]})
        with mock.patch(URLOPEN, return_value=reply):
            with self.assertRaises(RepositoryError):
                NpmRepository(BASE_URL).dependencies("p")


if __name__ == "__main__":
    unittest.main()
