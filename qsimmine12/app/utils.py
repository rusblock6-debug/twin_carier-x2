import os
import pathlib
import re
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

__all__ = (
    'TZ',
    'utc_now',
    'utc_to_enterprise',
    'enterprise_to_utc',
    'str_to_snake_case',
    'secure_filename',
    'human_size',
)

TZ = os.getenv('TZ')

# from werkzeug.utils import _filename_ascii_strip_re
_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")
_filename_unicode_strip_re = re.compile(r"[^\w.-]")
# from werkzeug.utils import _windows_device_files
_windows_device_files = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(10)),
    *(f"LPT{i}" for i in range(10)),
}


def utc_now():
    return datetime.now(timezone.utc)


def utc_to_enterprise(utc_time: str, tz: str = TZ) -> datetime:
    """Конвертирует UTC время в указанную таймзону"""
    return datetime.fromisoformat(utc_time.replace('Z', '+00:00'))\
                  .replace(tzinfo=timezone.utc)\
                  .astimezone(ZoneInfo(tz))


def enterprise_to_utc(local_time: str, tz: str = TZ) -> datetime:
    """Конвертирует локальное время предприятия в UTC"""
    return datetime.fromisoformat(local_time)\
                  .replace(tzinfo=ZoneInfo(tz))\
                  .astimezone(timezone.utc)


def str_to_snake_case(s: str) -> str:
    # Add an underscore before each uppercase letter that is followed by a lowercase letter
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    # Add an underscore before each lowercase letter that is preceded by an uppercase letter
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    # Convert the entire string to lowercase
    s = s.lower()
    return s


def secure_filename(filename: str, allow_unicode: bool = False) -> str:
    r"""Copy of :func:`werkzeug.utils.secure_filename`, but with `allow_unicode` arg

    Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    filename = unicodedata.normalize("NFKD", filename)
    if not allow_unicode:
        filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    if allow_unicode:
        strip_re = _filename_unicode_strip_re
    else:
        strip_re = _filename_ascii_strip_re
    filename = str(strip_re.sub("", "_".join(filename.split()))).strip(
        "._"
    )

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (
        os.name == "nt"
        and filename
        and filename.split(".")[0].upper() in _windows_device_files
    ):
        filename = f"_{filename}"

    return filename


def human_size(path: pathlib.Path) -> str:
    """Return human-readable file size"""
    size = path.stat().st_size
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size < 1024:
            return f'{size:.1f}{unit}'
        size /= 1024
    return f'{size:.1f}PB'
