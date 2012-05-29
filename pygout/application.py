from straight.plugin import load as plugin_load


class Application(object):
    @classmethod
    def name(cls):
        """Get the application's name.

        An application's canonical name is the lowercase name of the class
        implementing it.

        >>> Application().name()
        'application'
        """
        return cls.__name__.lower()


class PluginError(Exception):
    pass


def find_apps():
    plugins = plugin_load('pygout.apps', subclasses=Application)
    apps = {}

    for p in plugins:
        if p.name() in apps:
            raise PluginError(('Duplicate application name: '
                '{e.__module__}.{e.__name__} and '
                '{n.__module__}.{n.__name__}').format(e=apps[p.name()], n=p))
        else:
            apps[p.name()] = p

    return apps
