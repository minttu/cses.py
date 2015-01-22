import os
import sys
import requests
import multiprocessing
from os import path, makedirs
from subprocess import PIPE, Popen
from tempfile import gettempdir
from itertools import chain
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed


class Base(object):

    def __init__(self, name, file_extensions, template):
        self.name = name
        self.file_extensions = file_extensions
        self.template = template

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
        pool = Pool(processes=1)
        res = pool.apply_async(self._run, [cmd, filename, input])
        try:
            return res.get(timeout=3)
        except multiprocessing.context.TimeoutError:
            return "", "TIMEOUT", 1

    def _run(self, cmd, filename, input=None):
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

    def _prepare(self, filename):
        raise NotImplementedError()

    def _run_cmd(self, filename):
        raise NotImplementedError()

    def test(self, filename, tests):
        if tests["result"] != "ok":
            sys.stderr.write("Can't test this")
            sys.exit(1)
        print("Downloading tests")
        self.maketmp()
        self.download_tests(tests)
        out, err, code = self._prepare(filename)

        if len(err) > 0:
            sys.stderr.write(err + "\n")
        if code != 0:
            sys.exit(code)

        ok = True
        for test in tests["test"]:
            sys.stdout.write("#{} ".format(test["order"]))
            f_in = self.gettmp(test["input"])
            f_expected = self.gettmp(test["output"])
            c_in, c_expected = "", ""
            with open(f_in) as fp:
                c_in = fp.read()
            with open(f_expected) as fp:
                c_expected = fp.read()
            got, err, code = self.run(self._run_cmd(self.gettmp()),
                                      f_in, c_in)
            if len(err) > 0:
                sys.stderr.write("\n{}\n".format(err))
            sys.stdout.flush()
            sys.stderr.flush()
            if not self.compare(c_expected, got):
                ok = False
            else:
                print("OK\n")
        if not ok:
            sys.stderr.write("\nThere were some errors.\n")
            sys.exit(1)

    def compare(self, expected, got):
        if expected != got:
            # ToDo: Whitespace might be right even if different
            limit = 15
            sys.stderr.write("FAIL\nExpected:\n=========\n")
            expected_lines = expected.split("\n")
            sys.stderr.write("\n".join(expected_lines[:limit]))
            sys.stderr.write("\n")
            if len(expected_lines) > limit:
                sys.stderr.write("...\n")
            sys.stderr.write("\nGot:\n====\n")
            got_lines = got.split("\n")
            sys.stderr.write("\n".join(got_lines[:limit]))
            sys.stderr.write("\n")
            if len(got_lines) > limit:
                sys.stderr.write("...\n")
            sys.stderr.flush()
            return False
        return True
