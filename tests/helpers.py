"""Shared helpers for the tests."""


class RecordingView:
    """View that records everything shown to it."""

    def __init__(self):
        self.events = []

    def echo(self, prompt, line):
        """Record an echoed command line."""
        self.events.append(("echo", line))

    def out(self, text):
        """Record standard output."""
        self.events.append(("out", text))

    def err(self, text):
        """Record standard error."""
        self.events.append(("err", text))

    def kinds(self, kind):
        """Return the texts of all events of the given kind."""
        return [text for name, text in self.events if name == kind]
