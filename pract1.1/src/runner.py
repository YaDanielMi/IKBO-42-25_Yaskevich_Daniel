"""Glue between the shell and a view (GUI or console)."""


def show_result(result, view):
    """Show the output and the error of a Result in the view."""
    if result.output:
        view.out(result.output)
    if result.error:
        view.err(result.error)


def run_line(shell, line, view):
    """Echo a command line to the view, run it and show the result.

    The view must provide the methods echo(prompt, line), out(text)
    and err(text).
    """
    view.echo(shell.prompt(), line)
    result = shell.execute(line)
    show_result(result, view)
    return result
