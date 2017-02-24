import subprocess
import os

import Log

OVERLORD_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "OverlordCaller")
LOGGER = Log.MyLog(name=__name__)


def overlord(env="", tag="", params=""):
    workstation = "".join([s for s in os.environ['COMPUTERNAME'] if s.isdigit()])
    success = call(env,
                   tag,
                   params,
                   workstation)
    if success:
        return True
    else:
        log_error()
        return False


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
