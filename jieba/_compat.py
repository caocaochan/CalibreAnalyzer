import logging
import sys
from importlib.resources import files

log_console = logging.StreamHandler(sys.stderr)
default_logger = logging.getLogger(__name__)
default_logger.setLevel(logging.DEBUG)


def setLogLevel(log_level):
    default_logger.setLevel(log_level)


def get_module_res(*res):
    """Get resource file from package using importlib.resources (Python 3.9+)"""
    return files('jieba').joinpath(*res).open('rb')
    # return files(__name__).joinpath(*res).open('rb')


default_encoding = sys.getfilesystemencoding()

text_type = str
string_types = (str,)


def iterkeys(d):
    return iter(d.keys())


def itervalues(d):
    return iter(d.values())


def iteritems(d):
    return iter(d.items())


def strdecode(sentence):
    if not isinstance(sentence, text_type):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence


def resolve_filename(f):
    try:
        return f.name
    except AttributeError:
        return repr(f)
