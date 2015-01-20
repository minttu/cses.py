# coding: utf-8

cpptemplate = """#include <iostream>

using namespace std;

int main() {
    cin.sync_with_stdio(false);

    return 0;
}"""

class FileType(object):
    data = [
        ("C++", ["cpp", "pp", "p"], cpptemplate),
        ("Java", ["java"], ""),
        ("Python2", ["py", "py2"], ""),
        ("Python3", ["py3"], ""),
        ("Haskell", ["hs"], "")
    ]

    @staticmethod
    def detect(filename):
        for lang in FileType.data:
            if any([filename.endswith(x) for x in lang[1]]):
                return lang[0]
