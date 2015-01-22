from cses.tasks.base import Base

template = """-- task: {0}
main :: IO ()
main = putStrLn "??"
"""

class HaskellTask(Base):

    def __init__(self):
        super().__init__("Haskell", ["hs"], template)

    def _prepare(self, filename):
        return self.run(["ghc", "--make", "-o", self.gettmp(), filename],
                        filename, timeout=10)

    def _run_cmd(self, filename):
        return [filename]
