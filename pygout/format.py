from straight.plugin import load as plugin_load


class Format(object):
    @classmethod
    def name(cls):
        """Get the format's name.

        An format's canonical name is the lowercase name of the class
        implementing it.

        >>> Format().name()
        'format'
        """
        return cls.__name__.lower()

    @classmethod
    def qualified_name(cls):
        """Get the format's "qualified name", i.e. the full class and module
        name.  This is mostly useful in error messages about duplicate formats.
        """
        return '{cls.__module__}.{cls.__name__}'.format(cls=cls)

    def read(self, stream):
        """Read style from *stream* according to the format, returning a
        :class:`~pygout.style.SyntaxStyle`.
        """
        raise NotImplementedError

    def write(self, style, stream):
        """Write the :class:`~pygout.style.SyntaxStyle` *style* to *stream*
        according to the format.
        """
        raise NotImplementedError


class PluginError(Exception):
    pass


def find_formats():
    plugins = plugin_load('pygout.formats', subclasses=Format)
    formats = {}

    for p in plugins:
        if p.name() in formats:
            raise PluginError('Duplicate format: {e} and {n}'.format(
                    e=formats[p.name()].qualified_name(),
                    n=p.qualified_name()))
        else:
            formats[p.name()] = p

    return formats
