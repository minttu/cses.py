import shutil
from cses.tasks.base import Base

template = """#!/usr/bin/env python3
# task: {0}
"""

class Py3Task(Base):

    def __init__(self):
        super().__init__("Python3", ["py3"], template)

    def _prepare(self, filename):
        shutil.copy2(filename, self.getfile())
        return "", "", 0

    def _run_cmd(self, filename):
        return ["python3", filename]
