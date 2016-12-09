import time
import os

ERR_PATH = os.path.join(os.getcwd(), "Log")


def error(err_file, err_msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(ERR_PATH, err_file), 'a') as err:
        err.write("%s | %s\n" % (now, err_msg))

# # # #

if __name__ == "__main__":
    print ERR_PATH
