import os
import sys
import requests
from os import path, makedirs
from subprocess import PIPE, Popen
from tempfile import gettempdir
from itertools import chain
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed


class Base(object):

    def __init__(self, name, file_extensions, template):
        self.name = name
        self.file_extensions = file_extensions
        self.template = ""

    def gettmp(self, name="out"):
        tmp = path.join(gettempdir(), "cses", name)
        try:
            os.makedirs(path.split(tmp)[0])
        except OSError as e:
            pass
        return tmp

    def maketmp(self):
        try:
            os.makedirs(path.join(gettempdir(), "cses"))
        except OSError as e:
            pass

    def download_tests(self, tests):
        files = list(chain.from_iterable(("1/" + x["input"],
                                          "2/" + x["output"]) for x in tests["test"]))
        baseurl = "http://cses.fi/download/"

        def load(url):
            fname = path.join(gettempdir(), "cses", url.split("/")[1])
            if path.isfile(fname):
                return
            #if not path.exists(path.split(fname)):
            #    os.makedirs(fname)
            #open(fname, "w+").close()
            req = requests.get(baseurl + url)
            req.raise_for_status()
            with open(fname, "w") as fp:
                fp.write(req.text)
            return True

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(load, url): url for url in files}
            for future in as_completed(futures):
                future.result()

    def run(self, cmd, filename, input=None):
        try:
            ret = Popen(cmd,
                        stdout=PIPE,
                        stderr=PIPE,
                        stdin=PIPE,
                        cwd=path.split(filename)[0])
            if input != None:
                input = input.encode("utf-8")
            out, err = ret.communicate(input)
            return out.decode("utf-8"), err.decode("utf-8"), ret.returncode
        except OSError as e:
            if e.errno in [os.errno.ENOENT, os.errno.EACCES]:
                raise "No such program"
            else:
                raise e

    def applies_to(self, filename):
        return any([filename.endswith(x) for x in self.file_extensions])

    def _test(self, filename, tests):
        raise NotImplementedError()

    def test(self, filename, tests):
        if tests["result"] != "ok":
            sys.stderr.write("Can't test this")
            sys.exit(1)
        self.maketmp()
        self.download_tests(tests)
        self._test(filename, tests)


languages = []

def detect_type(filename):
    global languages
    if len(languages) == 0:
        languages = [c() for c in Base.__subclasses__()]
    return next(filter(lambda x: x.applies_to(filename), languages), None)
