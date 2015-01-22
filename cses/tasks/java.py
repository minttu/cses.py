import os
import sys
from cses.tasks.base import Base

template = """include java.util.*;

/**
 * Task: {0}
 */
public class {0} {{
    public static void main(string[] args) {{

    }}
}}
"""

class JavaTask(Base):

    def __init__(self):
        super().__init__("Java", ["java"], template)
