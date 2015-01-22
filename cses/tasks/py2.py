import shutil
from cses.tasks.base import Base

template = """#!/usr/bin/env python2
# task: {0}
"""

class Py2Task(Base):

    def __init__(self):
        super().__init__("Python2", ["py", "py2"], template)

    def _prepare(self, filename):
        shutil.copy2(filename, self.gettmp())
        return "", "", 0

    def _run_cmd(self, filename):
        return ["python2", filename]
