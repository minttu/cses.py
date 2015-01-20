# coding: utf-8

cpptemplate = """#include <iostream>

using namespace std;

/**
 * Task: {0}
 */
int main() {{
    cin.sync_with_stdio(false);

    return 0;
}}
"""

javatemplate = """include java.util.*;

/**
 * Task: {0}
 */
public class {0} {{
    public static void main(string[] args) {{

    }}
}}
"""

python2template = """#!/usr/bin/env python2
# task: {0}
"""

python3template = """#!/usr/bin/env python3
# task: {0}
"""

haskelltemplate = """#!/usr/bin/runghc
-- task: {0}
main :: IO ()
main = putStrLn "??"
"""

class FileType(object):
    data = [
        ("C++", ["cpp", "pp", "p"], cpptemplate),
        ("Java", ["java"], javatemplate),
        ("Python2", ["py", "py2"], python2template),
        ("Python3", ["py3"], python3template),
        ("Haskell", ["hs"], haskelltemplate)
    ]

    @staticmethod
    def detect(filename):
        for lang in FileType.data:
            if any([filename.endswith(x) for x in lang[1]]):
                return lang[0]
