class CSESError(Exception):

    def __init__(self, value="Undefined CSES error occured"):
        super().__init__()
        self.value = value

    def __str__(self):
        return self.value


class RunNoSuchProgramError(CSESError):

    def __init__(self, cmd):
        super().__init__("No such program as {}".format(cmd))


class RunTimeoutError(CSESError):

    def __init__(self, cmd, timeout):
        super().__init__("{} timed out in {}".format(cmd, timeout))


class APIError(CSESError):

    def __init__(self, value="Undefined API error occured"):
        super().__init__(value)
