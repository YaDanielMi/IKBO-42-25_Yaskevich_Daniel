"""Implementation of ls and cd on top of the in-memory VFS."""
from result import Result
from vfs import NOT_A_DIRECTORY, ROOT_PATH, CURRENT, PARENT, Node, VfsError

KNOWN_FLAGS = "al"
FLAG_ALL = "a"
FLAG_LONG = "l"
OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"
PREVIOUS_DIR = "-"


class OptionError(Exception):
    """Raised for unknown command options."""


def _split_flags(args):
    """Split ls arguments into (set of flag letters, list of paths)."""
    flags, paths, options_done = set(), [], False
    for arg in args:
        if options_done or arg == OPTION_PREFIX:
            paths.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        elif arg.startswith(END_OF_OPTIONS):
            raise OptionError(f"нераспознанный ключ '{arg}'")
        elif arg.startswith(OPTION_PREFIX):
            flags.update(arg[1:])
        else:
            paths.append(arg)
    unknown = sorted(flags - set(KNOWN_FLAGS))
    if unknown:
        raise OptionError(f"неверный ключ -- '{unknown[0]}'")
    return flags, paths


def _entries(node, flags):
    """Return the (name, node) pairs of a directory to be listed."""
    names = sorted(node.children)
    pairs = []
    if FLAG_ALL in flags:
        pairs = [(CURRENT, node), (PARENT, Node(PARENT, True))]
    else:
        names = [name for name in names if not name.startswith(".")]
    return pairs + [(name, node.children[name]) for name in names]


def _kind(node):
    """Return 'd' for directories and '-' for files."""
    return "d" if node.is_dir else "-"


def _format(entries, flags):
    """Format (name, node) pairs as a list of output lines."""
    if FLAG_LONG not in flags:
        return [name for name, _ in entries]
    width = max((len(str(node.size)) for _, node in entries), default=1)
    return [
        f"{_kind(node)} {node.size:>{width}} {name}"
        for name, node in entries
    ]


def _list_dir(node, path, flags, with_header):
    """Return the listing text of one directory argument of ls."""
    lines = _format(_entries(node, flags), flags)
    if with_header:
        lines.insert(0, f"{path}:")
    return "\n".join(lines)


def ls_in_vfs(shell, args):
    """List directories and files of the VFS (options -a and -l).

    As in ls, file arguments are printed first in one block, then each
    directory (with a "path:" header if there are several arguments).
    """
    try:
        flags, paths = _split_flags(args)
    except OptionError as error:
        return Result(error=f"ls: {error}")
    targets = paths or [CURRENT]
    files, chunks, errors = [], [], []
    for path in targets:
        try:
            _, node = shell.vfs.resolve(shell.cwd, path)
        except VfsError as error:
            message = f"ls: невозможно получить доступ к '{path}': {error}"
            errors.append(message)
            continue
        if node.is_dir:
            chunks.append(_list_dir(node, path, flags, bool(targets[1:])))
        else:
            files.append((path, node))
    if files:
        chunks.insert(0, "\n".join(_format(files, flags)))
    return Result(output="\n\n".join(chunks), error="\n".join(errors))


def _cd_target(shell, args):
    """Return (path to go to, whether to print it) for cd."""
    if not args:
        return ROOT_PATH, False
    if args[0] != PREVIOUS_DIR:
        return args[0], False
    if shell.oldpwd is None:
        raise VfsError("OLDPWD не задан")
    return shell.oldpwd, True


def cd_in_vfs(shell, args):
    """Change the working directory inside the VFS."""
    if args[1:]:
        return Result(error="cd: слишком много аргументов")
    try:
        target, show = _cd_target(shell, args)
        path, node = shell.vfs.resolve(shell.cwd, target)
        if not node.is_dir:
            raise VfsError(NOT_A_DIRECTORY)
    except VfsError as error:
        name = args[0] if args else ROOT_PATH
        return Result(error=f"cd: {name}: {error}")
    shell.oldpwd, shell.cwd = shell.cwd, path
    return Result(output=path if show else "")
