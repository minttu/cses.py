import os
import sys
import shutil
from os import path
from cses.tasks.base import Base

template = """import java.util.*;

/**
 * Task: {0}
 */
public class {0} {{
    public static void main(String[] args) {{

    }}
}}
"""

class JavaTask(Base):

    def __init__(self):
        super().__init__("Java", ["java"], template)
        self.ogname = ""

    def _prepare(self, filename):
        self.ogname = path.split(filename)[1].split(".")[0]
        dir = path.split(self.gettmp())[0]
        return self.run(["javac", "-d", dir, filename], filename)

    def _run_cmd(self, filename):
        return ["java", "-cp", ".", self.ogname]
