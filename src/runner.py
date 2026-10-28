"""Glue between the shell and a view (GUI or console)."""


def run_line(shell, line, view):
    """Echo a command line to the view, run it and show the result.

    The view must provide the methods echo(prompt, line), out(text)
    and err(text).
    """
    view.echo(shell.prompt(), line)
    result = shell.execute(line)
    if result.output:
        view.out(result.output)
    if result.error:
        view.err(result.error)
    return result
