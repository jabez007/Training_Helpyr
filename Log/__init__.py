import logging
import os

LOG_DIR = os.path.dirname(os.path.realpath(__file__))


class MyLog(logging.Logger):

    def __init__(self, name=__name__, level="INFO", file_ext="log"):
        """

        :param name:
        :param level: DEBUG, INFO, WARN, ERROR, CRITICAL - the logger will write everything at that level and down
        :param file_ext:
        """
        level = level.upper()
        log_level = getattr(logging, level, "INFO")
        logging.Logger.__init__(self, name, log_level)

        # create a file handler
        log_path = os.path.join(LOG_DIR, name)
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_filename = ".".join([level, file_ext])
        handler = logging.FileHandler(os.path.join(log_path, log_filename))
        handler.setLevel(log_level)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self.addHandler(handler)


class MyReader(object):

    def __init__(self, name=__name__, level="INFO", file_ext="log"):
        level = level.upper()
        self.log_filename = ""
        filename = os.path.join(LOG_DIR, name, ".".join([level, file_ext]))
        if os.path.isfile(filename):
            self.log_filename = filename

    def read(self):
        if self.log_filename:
            with open(self.log_filename, "r") as log_file:
                log = [line.strip() for line in log_file.readlines()]
            return reversed(log)
        return [""]

# # # #
