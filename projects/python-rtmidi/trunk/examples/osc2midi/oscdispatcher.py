# -*- coding: utf-8 -*-
#
# oscdispatcher.py
#
"""URL regex-based OSC message dispatching."""

__all__ = [
    'Pattern',
    'OSCDispatcher',
    'convert_bool',
    'main'
]

import logging
import re

from collections import namedtuple, OrderedDict
from functools import partial

try:
    from functools import lru_cache
except ImportError:
    # backport included with module
    from lru_cache import lru_cache


log = logging.getLogger(__name__)


def convert_bool(s):
    """Convert pseudo-boolean string values into Python boolean.

    If given argument is any of '1', 'enable', 'on', 't', 'true', 'y', or 'yes'
    it is considered True, else False.

    """
    return (True if s in ('1', 'enable', 'on', 't', 'true', 'y', 'yes')
        else False)

Pattern = namedtuple('Pattern',
    ('urlpattern', 'typecodes', 'funcname', 'convdict', 'userdata'))

class OSCDispatcher(list):
    """Dispatch OSC messages based on regular expression matching on path."""

    _rx_groupname = re.compile(r'\(\?P<([_a-zA-Z][:\w]*?)>(.*?)\)')
    _converters = {
        'f': float,
        'float': float,
        'i': int,
        'int': int,
        's': None,
        'str': None,
        'b': convert_bool,
        'bool': convert_bool
    }

    def __init__(self, patterns, search_ns=None, cache_size=0):
        """Initialize dispatcher with given patterns and set lookup namespace.

        For the structure of each pattern, see the docstring for the
        ``add_patterns`` method.

        ``search_ns`` is the namespace, in which handler and argument
        conversion functions are looked up. It can be any object, which
        supports attribute or dictionary with string keys lookup, e.g. a module
        object, a class instance, the dictionary returned by ``globals()`` or
        locals()`` or similar.

        """
        super(OSCDispatcher, self).__init__()
        self.add_patterns(patterns)
        self._cache_size = cache_size

        if cache_size != 0:
            self._get_pattern = lru_cache(cache_size)(self._get_pattern)

        if search_ns is None:
            self.search_ns = {}
        else:
            self.search_ns = search_ns

    def _get_pattern(self, path, typecodes):
        # Wrap cache lookup with method, so we can decorate it with 'lru_cache'
        for pattern in self:
            match = pattern.urlpattern.match(path)

            if match and typecodes == pattern.typecodes:
                return pattern, match

        raise KeyError("No matching pattern found.")

    def add_pattern(self, pattern):
        """Add given pattern to the dispatcher.

        A pattern must be a 3 or 4-element sequence of the form

        ::

            (urlpattern, typecodes, funcname[, userdata])

        where ``urlpattern`` is a regular expression for matching the path of
        incoming OSC messages, ``typecodes`` a string with OSC argument type
        codes and ``funcname`` the name of a handler function to call when
        an OSC message matches the URL pattern and has exactly the number and
        types of arguments specified in ``typecodes``.

        The handler function is looked up in the namespace passed to the
        constructor of this instance (see constructor docstring). The function
        should accept as many positional arguments as there are OSC types
        given in ``typecodes`` and keyword arguments for any named group in
        the URL pattern (see below for details).

        The pattern in ``urlpattern`` is a regular expression as understood
        by the standard Python ``re`` module with one important syntax
        extension. Groupnames can have the form ``prefix:name``, where name is
        the normal group name, which must be a valid Python identifier (no
        non-ASCII chars allowed though), and ``prefix`` is an identifier for
        conversion function, which is applied to the string matched by the
        group. This identifier can either refer to a builtin conversion
        function (see list below) or a callable found in the namespace passed
        to the constructor of this instance. The prefix is optional and, when
        left out, no conversion function is applied.

        OSC arguments are passed to the handler function as positional
        arguments and are converted to Python types according to their typecode
        (see the ``pyliblo`` documentation for the mapping between OSC and
        Python data types).

        Matches for named groups in the URL pattern are converted into keyword
        arguments to the handler function, with the name of the group as the
        keyword and the matched string as the value. If a name prefix is
        specified, the value is passed to the conversion function specified by
        the prefix and its return value is used as the value instead, unless
        an exception occurs in the conversion function.

        If the optional userdata is specified the fourth element of the
        pattern, it is passed to the handler function with the ``userdata``
        keyword argument. If group named ``userdata`` is matched by the URL
        pattern, its value has precedence.

        The builtin conversion identifiers and the functions they match to are
        as follows::

            {
                'i': int,
                'f': float,
                'int': int,
                'float': float,
                's': None,
                'str': None,
                'b': convert_bool,
                'bool': convert_bool,
            }

        See docstring for ``convert_bool`` function for its semantics.
        If a conversion identifier resolves to None, no conversion is applied.

        """
        try:
            urlpattern, typecodes, funcname, userdata = pattern
        except ValueError:
            urlpattern, typecodes, funcname = pattern
            userdata = None

        convdict = OrderedDict()
        repl = partial(self._store_and_remove_prefix, convdict=convdict)
        regex = re.compile(self._rx_groupname.sub(repl, urlpattern))
        self.append(
            Pattern(regex, typecodes, funcname, convdict, userdata))

    def add_patterns(self, patterns):
        """Add given list of patterns to the dispatcher.

        For the structure of each pattern, see the docstring for the
        ``add_pattern`` method.

        """
        for pattern in patterns:
            self.add_pattern(pattern)

    def _store_and_remove_prefix(self, match, convdict):
        """Replace 'prefix:name' with 'name' in a group pattern and store
        the prefix in convdict with name as key.

        """
        try:
            prefix, name = match.group(1).split(':', 1)
        except ValueError:
            name = match.group(1)
            prefix = None

        convdict[name] = prefix
        return '(?P<%s>%s)' % (name, match.group(2))

    def dispatch(self, path, args, typecodes, addr=None, userdata=None):
        """Dispatch one OSC message.

        Matches OSC path and argument types against stored patterns and
        calls the handler function of the first matching pattern.

        """

        try:
            pattern, match = self._get_pattern(path, typecodes)
        except KeyError:
            log.warning("No handler function found for OSC message (path=%r, "
                "args=%r, typecodes=%r, addr=%s)",
                path, args, typecodes, addr)
        else:
            try:
                func = getattr(self.search_ns, pattern.funcname, None)

                if not func:
                    func = self.search_ns[pattern.funcname]
            except (KeyError, TypeError):
                log.error("Handler function '%s' not found (namespace=%r).",
                    pattern.funcname, self.search_ns)
                return

            kwargs = self._convert_urlparams(pattern.convdict, match)

            if pattern.userdata:
                kwargs.setdefault('userdata', pattern.userdata)

            try:
                func(*args, **kwargs)
            except:
                funcname = getattr(func, 'func_name', func.__name__)
                log.exception("Exception in handler func '%s' (path=%r, "
                    "args=%r, kwargs=%r, typecodes=%r, addr=%s, "
                    "userdata=%r)", funcname, path, args, kwargs,
                    typecodes, addr, userdata)

    def _convert_urlparams(self, convdict, match):
        """Apply conversion function (if any) to all named groups in match.

        Returns a dictionary matching the group name to value, where the value
        is the string matched by the group, possibly converted by the function
        looked up in ``convdict``.

        """
        params = {}

        for name, value in match.groupdict().items():
            convspec = convdict.get(name)

            if convspec:
                try:
                    convfunc = getattr(self.search_ns, convspec, None)

                    if not convfunc:
                        convfunc = self._converters[convspec]
                except (AttributeError, KeyError):
                    log.error("Conversion func '%s' for param '%s' not found.",
                        convspec, name)
                else:
                    try:
                        if convfunc:
                            value = convfunc(value)
                    except:
                        log.exception("Exception in conversion func '%s' for "
                            "param '%s', value = %r", convspec, name, value)

            params[name] = value

        return params

    __call__ = dispatch


def main(args=None):
    """Test module by starting an OSC server on port 5555.

    Logs the arguments of all OSC messages with one float argument and
    a path like the following::

        /1/fader1
        /3/push2
        /2/rotary3

    which, incidentally, is what most messages sent by the TouchOSC
    application look like.

    A warning is logged for any OSC message not matched.

    """
    import time
    import liblo

    log = logging.getLogger('oscdispatcher')
    logging.basicConfig(level=logging.DEBUG)

    def log_call(*args, **kwargs):
        log.debug("Args: %r, kwargs=%r", args, kwargs)

    patterns = (
        (r'/(?P<i:page>\d+)/(?P<control>[a-z]+?)(?P<i:cc>\d+)$',
            'f', 'log_call'),
    )

    dispatcher = OSCDispatcher(patterns, search_ns=locals())

    class OSCTestServer(liblo.ServerThread):
        def __init__(self, dispatcher, port=5555):
            super(OSCTestServer, self).__init__(port)
            log.info("Listening on URL: " + self.get_url())
            self.add_method(None, None, dispatcher.dispatch)

    server = OSCTestServer(dispatcher)

    try:
        server.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        server.free()
        print('')

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]) or 0)
