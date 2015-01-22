from cses.tasks.base import Base

template = """-- task: {0}
main :: IO ()
main = putStrLn "??"
"""

class HaskellTask(Base):

    def __init__(self):
        super().__init__("Haskell", ["hs"], template)
