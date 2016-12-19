import MyTrack
import PowerShell
import Phonebook
import Overlord
import Log

MY_MODULES = ["Log", "Overlord", "MyTrack", "Phonebook", "PowerShell"]

# # # #
"""
Special setup for Care Everywhere 101 (fka CE-500)
"""


def ce500(instructor, trainees, code="CSCce500setup"):
    """
    entry point for setting up CE 101 (FKA CE500)
    :param instructor: <string> the cache environment for the Instructor
    :param trainees: <list(string)> the cache environments for the trainees
    :param code: <string> the Overlord tag the needs to be ran in each environment to complete setup
    :return: <bool> True if everything was successful
    """
    gwn = None
    trainees = clean_caches(trainees)

    if instructor:
        '''
        if this is a fresh class setup, as in we are not just adding trainee environments to an existing class
        '''
        # pull out the last trainee environment and make it GWN
        gwn = trainees[-1:]
        gwen(gwn)

        # then take that environment out of the list we'll set up later
        trainees = trainees[:-1]

        setup_instructor(instructor)

    # Connect Interconnects to trainee environments
    environment_pairs = assign_interconnects("CE500", trainees)
    if environment_pairs is None:
        return False

    # Update Training Phone Book with new environment assignments
    if not update_phonebook(trainees):
        return False

    # Restart the Training Phone Book so our changes take affect
    if not PowerShell.restart_phonebook():
        log_error("Error in restarting Training Phonebook Interconnect")
        return False

    # Run Cache setup script
    if not setup_cache([instructor]+trainees, code):
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
        log_error("Failed to connect epic-trn%s to CE500 instructor Interconnect. See powershell.err" % instructor)
        return False

    # Save to tracking database
    if not MyTrack.assign("Instructors", "train01", "epic-trn"+instructor):
        log_error("Setup between CE500 instructor Interconnect and epic-trn%s not saved to database. See my_track.err"
                  % instructor)

    # Reset TRN Phonebook and register Instructor environment
    if not Phonebook.TrnPhonebook().instructor(instructor):
        log_error("Error in registering epic-trn%s as the Instructor environment in the Training Phonebook. See TRNphonebook.err"
                  % instructor)
        return False

    return True


def update_phonebook(trainees):
    """
    updates the training Phonebook with trainee environments for this class
    :param trainees: <list(string)> the cache environments for the trainees
    :return: <bool> True if everything was successful
    """
    for cache in trainees:
        if not Phonebook.TrnPhonebook().register(cache):
            log_error("Error in registering epic-trn%s with Training Phonebook. See TRNphonebook.err" % cache)
            return False
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
    Phonebook.TrnPhonebook().register_gwn(trainee[0])
    # setup cache for GWN with the other environments
    return True

# # # #
"""
Generic Care Everywhere setup for IP and AMB Funds classes
"""


def funds(caches, code="CSCInpFunds"):
    caches = clean_caches(caches)

    if not assign_interconnects("AMB_IP", caches):
        return False

    if code:
        if not setup_cache(caches, code):
            return False

    return True

# # # #
"""
used by both Care Everywhere 101 and IP/AMB Funds
"""


def clean_caches(caches):
    return_caches = list()
    for c in caches:
        if c:  # Filter out blank lines
            cache = "".join([s for s in c if s.isdigit()])
            if cache:  # double check for blank lines
                return_caches.append(cache)
    return return_caches


def assign_interconnects(_class, caches):
    pairs = list()  # [(cache1, interconnect1), (cache2, interconnect2), ...]

    assigned_interconnects = 1  # CE500 instructor always gets Interconnect 1
    clss = _class
    for cache in caches:
        # #
        if ("CE500" in _class) and (assigned_interconnects >= 40):  # if training overbooks us, steal from FUNDs
            clss = "AMB_IP"
            interconnect = "".join([s for s in MyTrack.get("unassigned", "AMB_IP") if s.isdigit()])
        else:
            interconnect = "".join([s for s in MyTrack.get("unassigned", _class) if s.isdigit()])
        # #

        if interconnect:
            if not PowerShell.setup(interconnect, cache):
                log_error("Failed to connect epic-trn%s to train%s. See powershell.err" % (cache, interconnect))
                return None

            assigned_interconnects += 1
            pairs.append((cache, interconnect))

            if not MyTrack.assign(clss, "train"+interconnect, "epic-trn"+cache):
                log_error("Setup between epic-trn%s and train%s not saved to database. See my_track.err" % (cache, interconnect))
                return None

        else:
            log_error("No Interconnect returned for epic-trn%s. see my_track.err" % cache)
            return None

    return pairs


def setup_cache(trns, code, flag=""):
    if not Overlord.overlord(",".join(trns), code, flag):
        log_error("Error running %s. See cache.err" % code)
        return False

    return True


def log_error(msg):
    Log.error("setup.err",
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
    today = (datetime.datetime.now()).strftime("%m/%d/%Y")  # MM/DD/YYYY
    print("Setting up classes for %s:" % today)
    classes = MyTrack.setup_schedule(today)
    funds([_class[0] for _class in classes])
    for _class in classes:
        print("\t%s" % _class[0])
