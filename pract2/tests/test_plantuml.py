"""Tests for the PlantUML text and PNG rendering."""

import os
import tempfile
import unittest
from functools import cached_property
import urllib.error
from unittest import mock

from depgraph import plantuml
from depgraph.errors import RenderError

PNG = plantuml.PNG_SIGNATURE + b"data"
SAMPLE = "@startuml\nBob -> Alice : hello\n@enduml"
SAMPLE_CODE = "SoWkIImgAStDuNBAJrBGjLDmpCbCJbMmKiX8pSd9vt98pKi1IW80"
URLOPEN = "depgraph.plantuml.urllib.request.urlopen"


class PlantUmlTextTests(unittest.TestCase):
    """Generation of the PlantUML description."""

    def test_forward_graph(self):
        """Nodes are declared and arrows go from a package to its deps."""
        text = plantuml.to_plantuml({"A": ["B"], "B": []}, "A")
        self.assertEqual(
            text.splitlines(),
            [
                "@startuml",
                "title Dependencies of A",
                'rectangle "A" as n0 #LightBlue',
                'rectangle "B" as n1',
                "n0 --> n1",
                "@enduml",
            ],
        )

    def test_reverse_graph_swaps_arrows(self):
        """The edges of a reverse graph are drawn backwards."""
        text = plantuml.to_plantuml({"B": ["A"], "A": []}, "B", True)
        self.assertIn("title Reverse dependencies of B", text)
        self.assertIn("n1 --> n0", text)

    def test_scoped_names_are_quoted(self):
        """Special characters of npm names are safe inside quotes."""
        text = plantuml.to_plantuml({"@types/node": []}, "@types/node")
        self.assertIn('rectangle "@types/node" as n0', text)

    def test_cycle_edges(self):
        """Back edges of a cycle are drawn too."""
        text = plantuml.to_plantuml({"A": ["B"], "B": ["A"]}, "A")
        self.assertIn("n0 --> n1", text)
        self.assertIn("n1 --> n0", text)


class EncodingTests(unittest.TestCase):
    """Encoding for the PlantUML server."""

    def test_known_sample(self):
        """The result equals the example from the PlantUML documentation."""
        self.assertEqual(plantuml.encode_for_server(SAMPLE), SAMPLE_CODE)

    def test_alphabet(self):
        """Only characters of the PlantUML alphabet are produced."""
        code = plantuml.encode_for_server("x" * 100)
        self.assertTrue(set(code) <= set(plantuml.ALPHABET))


class RenderTests(unittest.TestCase):
    """Producing the PNG file."""

    @cached_property
    def output(self):
        """Path of the output file in a temporary directory."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return os.path.join(directory.name, "g.png")

    def read_output(self):
        """Return the content of the output file."""
        with open(self.output, "rb") as file:
            return file.read()

    def test_puml_path_and_text(self):
        """The text file has the name of the image with .puml."""
        path = plantuml.save_text("text", self.output)
        self.assertEqual(path, self.output[:-4] + ".puml")
        with open(path, encoding="utf-8") as file:
            self.assertEqual(file.read(), "text")

    def test_local_plantuml(self):
        """A local PlantUML is preferred when it is available."""
        result = mock.Mock(returncode=0, stdout=PNG, stderr=b"")
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("shutil.which", return_value="/bin/plantuml"), \
                mock.patch("subprocess.run", return_value=result) as run:
            plantuml.render_png("@startuml\n@enduml\n", self.output)
        self.assertEqual(run.call_args.args[0][0], "plantuml")
        self.assertEqual(self.read_output(), PNG)

    def test_jar_from_environment(self):
        """The PLANTUML_JAR variable selects java -jar."""
        result = mock.Mock(returncode=0, stdout=PNG, stderr=b"")
        with mock.patch.dict(os.environ, {"PLANTUML_JAR": "p.jar"}), \
                mock.patch("subprocess.run", return_value=result) as run:
            plantuml.render_png("text", self.output)
        self.assertEqual(run.call_args.args[0][:3], ["java", "-jar", "p.jar"])

    def test_local_failure(self):
        """A failing PlantUML is a render error."""
        result = mock.Mock(returncode=1, stdout=b"", stderr=b"Syntax Error")
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("shutil.which", return_value="/bin/plantuml"), \
                mock.patch("subprocess.run", return_value=result):
            with self.assertRaises(RenderError):
                plantuml.render_png("text", self.output)

    def test_server_fallback(self):
        """Without a local PlantUML the public server is used."""
        reply = mock.MagicMock()
        reply.__enter__.return_value.read.return_value = PNG
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("shutil.which", return_value=None), \
                mock.patch(URLOPEN, return_value=reply) as urlopen:
            plantuml.render_png(SAMPLE, self.output)
        self.assertEqual(
            urlopen.call_args.args[0], plantuml.SERVER_URL + SAMPLE_CODE
        )
        self.assertEqual(self.read_output(), PNG)

    def test_server_unreachable(self):
        """A network failure is a render error."""
        error = urllib.error.URLError("offline")
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("shutil.which", return_value=None), \
                mock.patch(URLOPEN, side_effect=error):
            with self.assertRaises(RenderError):
                plantuml.render_png("text", self.output)

    def test_not_a_png(self):
        """An answer that is not a PNG is rejected."""
        result = mock.Mock(returncode=0, stdout=b"<html>", stderr=b"")
        with mock.patch.dict(os.environ, {"PLANTUML_JAR": "p.jar"}), \
                mock.patch("subprocess.run", return_value=result):
            with self.assertRaises(RenderError):
                plantuml.render_png("text", self.output)
        self.assertFalse(os.path.exists(self.output))


if __name__ == "__main__":
    unittest.main()
