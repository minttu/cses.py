from cses.tasks.base import Base

template = """#!/usr/bin/env python3
# task: {0}
"""

class Py3Task(Base):

    def __init__(self):
        super().__init__("Py3", ["py3"], template)
