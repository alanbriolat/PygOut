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


class PluginError(Exception):
    pass


def find_formats():
    plugins = plugin_load('pygout.formats', subclasses=Format)
    formats = {}

    for p in plugins:
        if p.name() in formats:
            raise PluginError(('Duplicate format: '
                '{e.__module__}.{e.__name__} and '
                '{n.__module__}.{n.__name__}').format(e=formats[p.name()],
                                                      n=p))
        else:
            formats[p.name()] = p

    return formats
