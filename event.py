from collections import defaultdict


class Signal(object):
    def __init__(self, name=None):
        self.name = name
        self.__handlers = defaultdict(list)

    def connect(self, action, handler):
        self.__handlers[action].append(handler)

    def remove(self, action, handler):
        handlers = self.__handlers.get(action)

        if handlers:
            self.__handlers[action] = [func for func in handlers if func != handler]

    def fire(self, action, *args, **kwargs):
        handlers = self.__handlers.get(action)

        if handlers:
            for func in handlers:
                func(*args, **kwargs)

    def __repr__(self):
        return '{0.__class__.__name__}({0.name})'.format(self)

    def __str__(self):
        return '{0.__class__.__name__}({0.name}, {0.__handlers)'.format(self)
