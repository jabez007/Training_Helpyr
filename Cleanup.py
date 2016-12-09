import PowerShell
import MyTrack
import Phonebook
import Log

MY_MODULES = ["Log", "MyTrack", "Phonebook", "PowerShell"]


def ce500(instructor, trainees):
    if instructor:
        if not PowerShell.cleanup('01', instructor):
            log_error("Failed to clean-up: CE500 instructor Interconnect still connected to epic-trn%s" % instructor)
            return False
        
        if not MyTrack.unassign("Instructors", "train01"):
            log_error("Failed to save change to database: CE500 instructor Interconnect still taken by epic-trn%s" % instructor)

        if not Phonebook.TrnPhonebook().reset():
            log_error("Training Phonebook not reset")
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

    :param _class:
    :param trns: <tuple> (interconnect, cache)
    :return:
    """
    for trn in trns:
        if trn:
            interconnect = "".join([s for s in trn[0] if s.isdigit()])
            cache = "".join([s for s in trn[1] if s.isdigit()])

            if not PowerShell.cleanup(interconnect, cache):
                log_error("Failed clean-up: train%s still connected to epic-trn%s" % (interconnect, cache))
                # return False
        
            if not MyTrack.unassign(_class, "train"+interconnect):
                log_error("Failed to save change to database: train%s still taken by epic-trn%s" % (interconnect, cache))

    return True


def log_error(msg):
    Log.error("cleanup.err",
              msg)

# # # #


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    import types
    my_modules = [val for alias, val in globals().items()
                  if isinstance(val, types.ModuleType) and val.__name__ in MY_MODULES]
    for module in my_modules:
        module = reload(module)

    import datetime
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%m/%d/%Y")  # MM/DD/YYYY
    print("Cleaning up classes from %s:" % yesterday)
    classes = MyTrack.cleanup_schedule(yesterday)
    funds([MyTrack.get_funds("epic-trn"+_class[0]) for _class in classes])
    for _class in classes:
        print("\t%s" % _class[0])
