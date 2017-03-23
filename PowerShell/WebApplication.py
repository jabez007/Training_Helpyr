import re


class WebApplication(object):
    def __init__(self, ps_stdout):
        self.cache = InternalInt(0)
        self.interconnect = InternalInt(0)

        path = re.search('path\s*:(.+?)\n', ps_stdout)
        if path:
            self.cache = InternalInt("".join(c for c in path.group(1) if c.isdigit()))

        physical = re.search('PhysicalPath\s*:(.+?)\n', ps_stdout)
        if physical:
            self.interconnect = InternalInt("".join(c for c in physical.group(1) if c.isdigit()))

    def __str__(self):
        return "%s | %s" % (self.interconnect, self.cache)


class InternalInt(int):

    def __str__(self):
        if self < 10:
            return "0"+int(self).__str__()
        else:
            return int(self).__str__()

# # # #


if __name__ == "__main__":
    test1 = InternalInt("0004")
    print test1
    test2 = InternalInt("011")
    print test2
