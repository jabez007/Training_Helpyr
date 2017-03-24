import os
APP_PATH = os.path.join(*os.path.split(os.path.dirname(os.path.realpath(__file__)))[:-1])
import sys
if APP_PATH not in sys.path:
    sys.path.append(APP_PATH)

import PowerShell
import MyTrack
import Phonebook
import Log

LOGGER = Log.MyLog(name=__name__)


def ce500(instructor, trainees):
    if instructor:
        if not PowerShell.cleanup('01', instructor):
            LOGGER.error("Failed to clean-up: CE500 instructor Interconnect still connected to epic-trn%s" % instructor)
            return False
        
        if not MyTrack.unassign("Instructors", "train01"):
            LOGGER.error("Failed to save change to database: CE500 instructor Interconnect still taken by epic-trn%s" % instructor)

        if not Phonebook.TrnPhonebook().reset():
            LOGGER.error("Training Phonebook not reset")
            return False

    if not unassign_interconnects("CE500", trainees):
        return False

    return True


def funds(trainees):
    if not unassign_interconnects("AMB_IP", trainees):
        return False

    return True

# # # #


def unassign_interconnects(_class, trns):
    """

    :param _class: <string>
    :param trns: <list(tuple)> [(interconnect, cache)]
    :return:
    """
    total_success = True
    for trn in trns:
        this_success = True
        if trn:
            interconnect = "".join([s for s in trn[0] if s.isdigit()])
            cache = "".join([s for s in trn[1] if s.isdigit()])

            if not PowerShell.cleanup(interconnect, cache):
                LOGGER.error("Failed clean-up: train%s still connected to epic-trn%s" % (interconnect, cache))
                total_success = False
                this_success = False
        
            if not MyTrack.unassign(_class, "train"+interconnect):
                LOGGER.error("Failed to save change to database: train%s still taken by epic-trn%s" % (interconnect, cache))
                total_success = False
                this_success = False

            if this_success:
                LOGGER.info("epic-trn%s successfully cleaned up" % cache)

    return total_success


# # # #


if __name__ == "__main__":
    import datetime

    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")  # MM/DD/YYYY
    print("Cleaning up classes from %s:" % yesterday)

    classes = MyTrack.cleanup_schedule(yesterday)
    funds([MyTrack.get_funds("epic-trn"+_class[0]) for _class in classes])
    for _class in classes:
        print("\t%s" % _class[0])
