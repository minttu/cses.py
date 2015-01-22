import cses.tasks.base
import cses.tasks.cpp
import cses.tasks.java
import cses.tasks.py2
import cses.tasks.py3
import cses.tasks.hs

from cses.tasks.base import Base

languages = [c() for c in Base.__subclasses__()]

def detect_type(filename):
    return next(filter(lambda x: x.applies_to(filename), languages), None)
