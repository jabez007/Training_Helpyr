import subprocess
import os
import re

import Log

OVERLORD_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "OverlordCaller")
LOGGER = Log.MyLog(name=__name__)


def ce_diags(env=""):
    return overlord(env, tag="CSCDiag")


def overlord(env="", tag="", params=""):
    workstation = "".join([s for s in os.environ['COMPUTERNAME'] if s.isdigit()])
    success = call(clean_caches(env),
                   tag,
                   params,
                   workstation)
    if success:
        LOGGER.info("%s successfully ran in %s" % (tag, env))
        return True
    else:
        log_error()
        return False


def clean_caches(caches):
    """
    uses regex to parse out our cache environments passed in
    :param caches: <string> 
    :return: <list(string)>
    """

    return_caches = list()

    data = re.finditer("([a-zA-Z0-9\-]+)", caches)
    for d in data:
        cache = "".join([s for s in d.group(1) if s.isdigit()])
        if cache:
            return_caches.append(cache)

    return ",".join(return_caches)


def call(env, tag, params, ws=""):
    p = subprocess.Popen([os.path.join(OVERLORD_PATH, 'OverlordCaller.exe'),
                          '-environment', env,
                          '-workstation', ws,
                          '-tag', tag,
                          '-optvars', params],
                         cwd=OVERLORD_PATH)
    result = p.wait()
    return result


def log_error():
    with open(os.path.join(OVERLORD_PATH, "details.txt"), 'r') as inf:
        details_list = [detail.strip() for detail in inf.readlines()]

    for detail in details_list:
        msg = "%s: %s" % tuple(detail.split("|"))
        LOGGER.error(msg)

# # # #

if __name__ == "__main__":
    print OVERLORD_PATH

    trns = "".split(",")
    for trn in trns:
        if not overlord(trn, "CSCDoStuff"):
            with open(os.path.join(OVERLORD_PATH, "details.txt"), 'r') as err:
                print err.read()
