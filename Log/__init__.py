import time
import os

import sys
sys.path.append(r"F:\personal\jwmccann\Python\Personal\MyLib.py")
from MyLog import MyLog


ERR_PATH = os.path.dirname(os.path.realpath(__file__))
LOGS = dict()


def error(err_name, err_msg):
    global LOGS

    if "ERRORS" not in LOGS:
        LOGS["ERRORS"] = dict()

    if err_name not in LOGS["ERRORS"]:
        LOGS["ERRORS"][err_name] = MyLog(name=err_name, level="ERROR")

    LOGS["ERRORS"][err_name].error(err_msg)


def info(info_name, info_msg):
    global LOGS

    if "INFO" not in LOGS:
        LOGS["INFO"] = dict()

    if info_name not in LOGS["INFO"]:
        LOGS["INFO"][info_name] = MyLog(name=info_name)

    LOGS["INFO"][info_name].info(info_msg)


def debug(debug_name, debug_msg):
    global LOGS

    if "DEBUG" not in LOGS:
        LOGS["DEBUG"] = dict()

    if debug_name not in LOGS["DEBUG"]:
        LOGS["DEBUG"][debug_name] = MyLog(name=debug_name)

    LOGS["DEBUG"][debug_name].info(debug_msg)

# # # #

if __name__ == "__main__":
    print ERR_PATH
