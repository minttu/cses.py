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

    def _test(self, filename, tests):
        out, err, code = self.run(self.compile_cmd + [self.gettmp(), filename],
                                  filename)
        if code != 0:
            sys.stderr.write(err + "\n")
            sys.exit(code)

        if len(err) > 0:
            sys.stderr.write(err + "\n")

        for test in tests["test"]:
            sys.stdout.write("#{} ".format(test["order"]))
            fin = self.gettmp(test["input"])
            fint = ""
            with open(fin) as fp:
                fint = fp.read()
            fout = self.gettmp(test["output"])
            foutt = ""
            with open(fout) as fp:
                foutt = fp.read()

            out, err, code = self.run([self.gettmp()], fin, fint)
            if code != 0:
                sys.stderr.write("\n" + err + "\n")
                sys.exit(code)

            if len(err) > 0:
                sys.stderr.write("\n" + err + "\n")

            if foutt != out:
                sys.stdout.write("FAIL\n")
            else:
                sys.stdout.write("OK\n")
