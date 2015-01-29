import os
import sys
import requests
import multiprocessing
import click
import time

from os import path, makedirs
from subprocess import PIPE, Popen
from itertools import chain
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from threading import Thread

from cses.errors import RunTimeoutError, RunNoSuchProgramError


class Run(object):
    def __init__(self, cmd, cwd, input=None, timeout=3):
        self.cmd = cmd
        self.cwd = cwd
        if input != None:
            input = input.encode("utf-8")
        self.input = input
        self.process = None
        self.out = b""
        self.err = b""
        self.timeout = timeout
        self.exception = None

    def run(self):
        def target():
            try:
                self.process = Popen(self.cmd,
                                     stdout=PIPE,
                                     stderr=PIPE,
                                     stdin=PIPE,
                                     cwd=self.cwd)
                self.out, self.err = self.process.communicate(self.input)
            except OSError as e:
                if e.errno in [os.errno.ENOENT, os.errno.EACCES]:
                    self.exception = RunNoSuchProgramError(self.cmd[0])
                else:
                    self.exception = e

        thread = Thread(target=target)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            return "", "TIMEOUT", 1

        if self.exception is not None:
            raise self.exception

        return (self.out.decode("utf-8"),
                self.err.decode("utf-8"),
                self.process.returncode)


class Result(object):

    def __init__(self, testid, stderr="", input="", got="", expected="",
                 full=False):
        self.testid = testid
        self.warning = stderr
        self.input = input
        self.got = got
        self.expected = expected
        self.full = full
        self.success = got == expected
        self.message = "ok\n" if self.success else "fail\n"

    def __str__(self):
        def ens(str):
            return str if str.endswith("\n") else str + "\n"

        def title(str):
            return "|> {}\n".format(str)

        def show(str):
            if not self.full:
                nl_num = str[:200].count("\n")
                if nl_num >= 15:
                    return "\n".join(str.split("\n")[:15]) + "\n...\n"
                return str[:200] if len(str) < 200 else str[:200] + "\n...\n"
            return str

        msg = "|> Test #{} {}".format(self.testid, self.message)
        if self.warning != "":
            msg += ens(self.warning)
        if not self.success and len(self.input) > 0:
            msg += title("Input")
            msg += show(self.input)
            msg += title("Correct output")
            msg += show(self.expected)
            msg += title("Your output")
            msg += show(self.got)

        return msg


class Base(object):

    def __init__(self, name, file_extensions, template):
        self.name = name
        self.file_extensions = file_extensions
        self.template = template

    def getdir(self):
        return path.join(path.expanduser("~"), ".cses")

    def getfile(self, name="out"):
        return path.join(self.getdir(), name)

    def makedir(self):
        makedirs(self.getdir(), mode=0o700, exist_ok=True)

    def download_tests(self, tests):
        duplicate_files = list(chain.from_iterable(((1, x["input"]),
                                                    (2, x["output"]))
                                                   for x in tests["test"]))
        files = []
        for file in duplicate_files:
            if file[1] not in files:
                files.append(file)

        baseurl = "http://cses.fi/download/"

        def load(dir, hash):
            fname = self.getfile(hash)
            if path.isfile(fname):
                return
            req = requests.get("{}{}/{}".format(baseurl, dir, hash))
            req.raise_for_status()
            with open(fname, "w") as fp:
                fp.write(req.text)
            return True

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(load, f[0], f[1]): f for f in files}
            for future in as_completed(futures):
                yield future.result()

    def run(self, cmd, cwd=None, input=None, timeout=3):
        if cwd is None:
            cwd = self.getdir()
        return Run(cmd=cmd, cwd=cwd, input=input, timeout=timeout).run()

    def applies_to(self, filename):
        return any([filename.endswith(x) for x in self.file_extensions])

    def _prepare(self, filename):
        raise NotImplementedError()

    def _run_cmd(self, filename):
        raise NotImplementedError()

    def user_run(self, filename):
        self.makedir()
        print("|> Preparing")
        out, err, code = self._prepare(filename)

        if len(err) > 0:
            sys.stderr.write(err + "\n")
        if code != 0:
            sys.exit(code)

        cmd = self._run_cmd(self.getfile())
        print("|> Running {}".format(" ".join(cmd)))
        ret = Popen(cmd, cwd=self.getdir())
        code = ret.communicate()
        sys.exit(ret.returncode)

    def test(self, filename, tests, keep_going, full):
        if tests["result"] != "ok":
            sys.stderr.write("Can't test this")
            sys.exit(1)
        self.makedir()

        with click.progressbar(self.download_tests(tests),
                               length=len(tests["test"]) * 2,
                               label="|> Downloading tests") as downloads:
            for dl in downloads:
                pass

        print("|> Preparing code")

        out, err, code = self._prepare(filename)

        if len(err) > 0:
            sys.stderr.write(err + "\n")
        if code != 0:
            sys.exit(code)

        returns = []

        with click.progressbar(tests["test"],
                               label="|> Running tests") as tests:
            for test in tests:
                f_in = self.getfile(test["input"])
                f_expected = self.getfile(test["output"])

                input, c_expected = "", ""
                with open(f_in) as fp:
                    input = fp.read()
                with open(f_expected) as fp:
                    expected = fp.read()

                got, err, code = self.run(self._run_cmd(self.getfile()),
                                          input=input)

                result = Result(test["order"], err, input, got, expected, full)
                returns.append(result)

                if not result.success and not keep_going:
                    break

        ok = True
        for res in returns:
            if not res.success:
                ok = False
                print(res)

        if not ok:
            print("There were some errors")
            sys.exit(1)
        else:
            print("All OK!")

    def compare(self, expected, got):
        return expected == got
