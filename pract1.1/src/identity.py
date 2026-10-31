"""Information about the real operating system user and host."""
import getpass
import socket

FALLBACK_USER = "user"
TITLE_TEMPLATE = "Эмулятор - [{user}@{host}]"


def get_identity():
    """Return the pair (username, hostname) of the real OS."""
    try:
        user = getpass.getuser()
    except (KeyError, OSError):
        user = FALLBACK_USER
    return user, socket.gethostname()


def window_title(user, host):
    """Build the window title from the real user and host names."""
    return TITLE_TEMPLATE.format(user=user, host=host)
