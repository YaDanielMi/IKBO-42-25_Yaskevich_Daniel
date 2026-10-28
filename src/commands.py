"""Built-in commands of the shell emulator."""
from result import Result
from vfs_commands import cd_in_vfs, ls_in_vfs

EXIT_CODE_MODULO = 256
EXIT_BAD_ARGUMENT = 2


def stub(name, args):
    """Return a Result printing the command name and its arguments."""
    return Result(output=f"{name}: заглушка, аргументы: {args!r}")


def cmd_ls(shell, args):
    """List directory contents (a stub when no VFS is connected)."""
    if shell.vfs is None:
        return stub("ls", args)
    return ls_in_vfs(shell, args)


def cmd_cd(shell, args):
    """Change directory (a stub when no VFS is connected)."""
    if shell.vfs is None:
        return stub("cd", args)
    return cd_in_vfs(shell, args)


def cmd_exit(shell, args):
    """Terminate the emulator, optionally with a numeric exit code."""
    if not args:
        return Result(exit_requested=True)
    if args[1:]:
        return Result(error="exit: слишком много аргументов")
    try:
        code = int(args[0])
    except ValueError:
        return Result(
            error=f"exit: {args[0]}: требуется числовой аргумент",
            exit_requested=True,
            exit_code=EXIT_BAD_ARGUMENT,
        )
    return Result(exit_requested=True, exit_code=code % EXIT_CODE_MODULO)


COMMANDS = {"ls": cmd_ls, "cd": cmd_cd, "exit": cmd_exit}
