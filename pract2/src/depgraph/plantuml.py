"""PlantUML description of a graph and its rendering into a PNG file.

The PNG is produced by a local PlantUML (the ``plantuml`` command or the
jar given in the ``PLANTUML_JAR`` environment variable) and, if there is
none, by the public PlantUML server.
"""

import http.client
import os
import shutil
import subprocess
import urllib.error
import urllib.request
import zlib

from depgraph.errors import RenderError

SERVER_URL = "https://www.plantuml.com/plantuml/png/"
JAR_ENV = "PLANTUML_JAR"
LOCAL_COMMAND = "plantuml"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
TIMEOUT_SECONDS = 60
ROOT_COLOR = " #LightBlue"
ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz-_"
)
GROUP_SIZE = 3


def to_plantuml(graph, root, reverse=False):
    """Return the PlantUML text of the graph.

    An arrow ``A --> B`` always means "A depends on B", so the edges of a
    reverse graph are drawn in the opposite direction.
    """
    kind = "Reverse dependencies" if reverse else "Dependencies"
    ids = {name: f"n{index}" for index, name in enumerate(graph)}
    lines = ["@startuml", f"title {kind} of {root}"]
    for name, alias in ids.items():
        color = ROOT_COLOR if name == root else ""
        lines.append(f'rectangle "{name}" as {alias}{color}')
    for name, neighbours in graph.items():
        for other in neighbours:
            source, target = (other, name) if reverse else (name, other)
            lines.append(f"{ids[source]} --> {ids[target]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def puml_path(output):
    """Return the path of the text file that goes next to the image."""
    return os.path.splitext(output)[0] + ".puml"


def save_text(text, output):
    """Save the PlantUML text next to the image and return its path."""
    path = puml_path(output)
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
    except OSError as error:
        raise RenderError(f"cannot write {path}: {error}") from error
    return path


def _encode_group(first, second, third):
    """Encode three bytes into four characters of the PlantUML alphabet."""
    indexes = (
        first >> 2,
        ((first & 0x3) << 4) | (second >> 4),
        ((second & 0xF) << 2) | (third >> 6),
        third & 0x3F,
    )
    return "".join(ALPHABET[index] for index in indexes)


def encode_for_server(text):
    """Compress and encode the text the way the PlantUML server expects."""
    compressor = zlib.compressobj(
        zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, -zlib.MAX_WBITS
    )
    data = compressor.compress(text.encode("utf-8")) + compressor.flush()
    data += bytes(-len(data) % GROUP_SIZE)
    return "".join(
        _encode_group(*data[start:start + GROUP_SIZE])
        for start in range(0, len(data), GROUP_SIZE)
    )


def _local_command():
    """Return the command of a local PlantUML or None if it is missing."""
    jar = os.environ.get(JAR_ENV)
    if jar:
        return ["java", "-jar", jar, "-tpng", "-pipe"]
    if shutil.which(LOCAL_COMMAND):
        return [LOCAL_COMMAND, "-tpng", "-pipe"]
    return None


def _render_local(command, text):
    """Render the diagram with a locally installed PlantUML."""
    try:
        result = subprocess.run(
            command, input=text.encode("utf-8"), capture_output=True,
            timeout=TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise RenderError(f"cannot run PlantUML: {error}") from error
    if result.returncode:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise RenderError(f"PlantUML failed: {message}")
    return result.stdout


def _render_remote(text):
    """Render the diagram with the public PlantUML server."""
    url = SERVER_URL + encode_for_server(text)
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as reply:
            return reply.read()
    except (OSError, ValueError, http.client.HTTPException) as error:
        raise RenderError(
            f"PlantUML server request failed: {error}. Install PlantUML "
            f"or set {JAR_ENV}, or use the saved .puml file"
        ) from error


def render_png(text, output):
    """Render the PlantUML text into the PNG file."""
    command = _local_command()
    data = _render_local(command, text) if command else _render_remote(text)
    if not data.startswith(PNG_SIGNATURE):
        raise RenderError("PlantUML did not return a PNG image")
    try:
        with open(output, "wb") as file:
            file.write(data)
    except OSError as error:
        raise RenderError(f"cannot write {output}: {error}") from error
