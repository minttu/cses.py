import os
import sys
from cses.tasks.base import Base

template = """#include <iostream>

using namespace std;

/**
 * Task: {0}
 */
int main() {{
    cin.sync_with_stdio(false);

    return 0;
}}
"""

class CPPTask(Base):

    def __init__(self):
        super().__init__("C++", ["cpp", "cc", "c"], template)
        self.compile_cmd = ["g++", "-std=c++0x", "-O2", "-Wall", "-o"]

    def _prepare(self, filename):
        return self.run(self.compile_cmd + [self.gettmp(), filename], filename)

    def _run_cmd(self, filename):
        return [filename]
