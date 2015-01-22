from cses.tasks.base import Base

template = """#!/usr/bin/env python2
# task: {0}
"""

class Py2Task(Base):

    def __init__(self):
        super().__init__("Python2", ["py", "py2"], template)
