import atexit
import shelve
import click

from os import path

class DB(object):
    def __init__(self):
        data = shelve.open(path.join(path.expanduser("~"),
                                     ".config",
                                     "cses"),
                           writeback=True)
        super().__setattr__("shelve", data)
        atexit.register(data.close)

    def __getattr__(self, name):
        return self.shelve.get(name)

    def __setattr__(self, name, value):
        self.shelve[name] = value


give_db = click.make_pass_decorator(DB, ensure=True)
