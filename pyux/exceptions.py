class APIChangedException(Exception):
    def __init__(self, diff):
        self.diff = diff

    def __str__(self):
        if isinstance(self.diff, str):
            return self.diff
        return '\n'.join([str(x) for x in self.diff])

