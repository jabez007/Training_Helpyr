import re


class WebApplication(object):
    def __init__(self, ps_stdout):
        self.cache = 0
        self.interconnect = 0

        path = re.search('path\s*:(.+?)\n', ps_stdout)
        if path:
            self.cache = int("".join(c for c in path.group(1) if c.isdigit()))

        physical = re.search('PhysicalPath\s*:(.+?)\n', ps_stdout)
        if physical:
            self.interconnect = int("".join(c for c in physical.group(1) if c.isdigit()))

    def __str__(self):
        return "%s | %s" % (self.interconnect, self.cache)
