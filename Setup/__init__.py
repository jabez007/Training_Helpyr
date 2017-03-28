import re
import os
APP_PATH = os.path.join(*os.path.split(os.path.dirname(os.path.realpath(__file__)))[:-1])
import sys
if APP_PATH not in sys.path:
    sys.path.append(APP_PATH)

import MyTrack
import PowerShell
import Phonebook
import Overlord
import Log

LOGGER = Log.MyLog(name=__name__)

# # # #
"""
Special setup for Care Everywhere 101 (fka CE-500)
"""


def ce500(instructor, trainees, code="CSCce500setup"):
    """
    entry point for setting up CE 101 (FKA CE500)
    :param instructor: <string> the cache environment for the Instructor
    :param trainees: <string> the cache environments for the trainees
    :param code: <string> the Overlord tag the needs to be ran in each environment to complete setup
    :return: <bool> True if everything was successful
    """
    gwn = None
    instr = "".join([c for c in instructor if c.isdigit()])
    trns = clean_caches(trainees)

    if instr:
        '''
        if this is a fresh class setup, as in we are not just adding trainee environments to an existing class
        '''
        # pull out the last trainee environment and make it GWN
        gwn = trns[-1:]
        if gwen(gwn):
            # then take that environment out of the list we'll set up later
            trns = trns[:-1]
            LOGGER.info("epic-trn%s set up as GWN environment" % gwn[0])
        else:
            # otherwise, skip the GWN setup and make this a normal environment
            gwn = None
            LOGGER.error("Galaxy Wide Network not set up")

        setup_instructor(instr)

    # Connect Interconnects to trainee environments
    environment_pairs = assign_interconnects("CE500", trns)
    if environment_pairs is None:
        return False

    # Update Training Phone Book with new environment assignments
    if not update_phonebook(trns):
        return False

    # Restart the Training Phone Book so our changes take affect
    if not PowerShell.restart_phonebook():
        LOGGER.error("Error in restarting Training Phonebook Interconnect")
        return False

    # Run Cache setup script
    if not setup_cache([instr]+trns, code):
        return False
    if gwn is not None:
        setup_cache(gwn, code, "GWeN")

    return True


def setup_instructor(instructor):
    """
    runs the setup particular to the instructor environment
    :param instructor: <string> the cache environment for the class instructor
    :return: <bool> True is everything was successful
    """
    # Connect Interconnect to instructor environment
    if not PowerShell.setup('01', instructor):
        LOGGER.error("Failed to connect epic-trn%s to CE500 instructor Interconnect. See powershell.err" % instructor)
        return False

    # Save to tracking database
    if not MyTrack.assign("Instructors", "train01", "epic-trn"+instructor):
        LOGGER.error("Setup between CE500 instructor Interconnect and epic-trn%s not saved to database. See my_track.err"
                     % instructor)

    # Reset TRN Phonebook and register Instructor environment
    if not Phonebook.TrnPhonebook().instructor(instructor):
        LOGGER.error("Error in registering epic-trn%s as the Instructor environment in the Training Phonebook. See TRNphonebook.err"
                     % instructor)
        return False

    LOGGER.info("epic-trn%s set up as instructor environment" % instructor)
    return True


def update_phonebook(trainees):
    """
    updates the training Phonebook with trainee environments for this class
    :param trainees: <list(string)> the cache environments for the trainees
    :return: <bool> True if everything was successful
    """
    for cache in trainees:
        if not Phonebook.TrnPhonebook().register(cache):
            LOGGER.error("Error in registering epic-trn%s with Training Phonebook. See TRNphonebook.err" % cache)
            return False
    LOGGER.info("Trainee environments registered in phonebook")
    return True


def gwen(trainee):
    """
    runs the setup particular to the Galaxy Wide Network environment
    :param trainee: <string> the cache environment for GWN
    :return: <bool> True if everything was successful
    """
    # assign interconnect - this should be the same as the other trainee environments
    assign_interconnects("CE500", trainee)
    # update Phonebook
    if not Phonebook.TrnPhonebook().register_gwn(trainee[0]):
        return False
    # setup cache for GWN with the other environments
    return True

# # # #
"""
Generic Care Everywhere setup for IP and AMB Funds classes
"""


def funds(caches, code="CSCInpFunds"):
    """
    
    :param caches: <string> 
    :param code: <string>
    :return: <bool>
    """
    trns = clean_caches(caches)

    if not assign_interconnects("AMB_IP", trns):
        return False

    if code:
        if not setup_cache(trns, code):
            return False

    return True

# # # #
"""
used by both Care Everywhere 101 and IP/AMB Funds
"""


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

    return return_caches


def assign_interconnects(_class, trns):
    pairs = list()  # [(cache1, interconnect1), (cache2, interconnect2), ...]

    assigned_interconnects = 1  # CE500 instructor always gets Interconnect 1
    clss = _class
    for cache in trns:
        # #
        if ("CE500" in _class) and (assigned_interconnects >= 40):  # if training overbooks us, steal from FUNDs
            clss = "AMB_IP"
            interconnect = "".join([s for s in MyTrack.get("unassigned", "AMB_IP") if s.isdigit()])
        else:
            interconnect = "".join([s for s in MyTrack.get("unassigned", _class) if s.isdigit()])
        # #

        if interconnect:
            if not PowerShell.setup(interconnect, cache):
                LOGGER.error("Powershell failed to connect epic-trn%s to train%s" % (cache, interconnect))
                return None

            assigned_interconnects += 1
            pairs.append((cache, interconnect))

            if not MyTrack.assign(clss, "train"+interconnect, "epic-trn"+cache):
                LOGGER.error("Setup between epic-trn%s and train%s not saved to MyTrack" % (cache, interconnect))
                return None

        else:
            LOGGER.error("No Interconnect returned from MyTrack for epic-trn%s" % cache)
            return None

        LOGGER.info("epic-trn%s connected to Interconnect-train%s" % (cache, interconnect))

    return pairs


def setup_cache(trns, code, flag=""):
    success = True
    for trn in trns:
        if not Overlord.overlord(trn, code, flag):
            LOGGER.error("Error running %s. See Overlord logs" % code)
            success = False
    # LOGGER.info("%s successfully ran in %s" % (code, ", ".join(trns)))
    return success

# # # #


if __name__ == "__main__":
    import datetime
    import Outlook

    today = (datetime.datetime.now()).strftime("%m/%d/%Y")  # MM/DD/YYYY
    print("Setting up classes for %s:" % today)

    classes = MyTrack.setup_schedule(today)
    for new_class in classes:
        if funds(new_class[0]):
            print("\t%s - email to %s" % (new_class[0], new_class[1]))
            Outlook.send_email(e_address=new_class[1], env=new_class[0])
        else:
            print("\t%s failed" % new_class[0])
