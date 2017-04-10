# -*- coding: utf-8 -*-
import win32com.client
import re
import datetime
import pywintypes

import MyTrack
from Log import MyLog

LOGGER = MyLog(name="Outlook")


def find_requests():
    requested_environments = list()
    if datetime.datetime.today().weekday() == 0:  # it's the Monday blues
        # search all the way back to Friday
        back_to = pywintypes.Time((datetime.datetime.now() - datetime.timedelta(days=3)).timetuple())
    else:
        # just search back to yesterday
        back_to = pywintypes.Time((datetime.datetime.now() - datetime.timedelta(days=1)).timetuple())

    LOGGER.info("Searching HDRs that came in since %s" % back_to)

    obj = win32com.client.Dispatch("Outlook.Application")
    outlook = obj.GetNamespace("MAPI")
    mail = outlook.GetDefaultFolder(6)
    '''
    "6" refers to the index of a folder - in this case, the Inbox/Mail folder (as opposed to the Calender folder).
    You can change that number to reference any other folder.
    '''
    hdr_folder_path = r"\\jwmccann@epic.com\Inbox\Care Everywhere\TS\Camp\HDR"  # Change this to change where we search
    hdr_folder = get_folder_by_path(mail, hdr_folder_path)
    hdr_requests = hdr_folder.Items  # list of MailItem objects
    for request in hdr_requests:
        if request.ReceivedTime >= back_to:  # received in the last 24 hours
            hdr = read_hdr(request.Body)

            LOGGER.info("Found %s" % str(hdr))

            requested_environments.append(hdr)
            request.UnRead = False
            request.Save()

    return requested_environments


def get_folder_by_path(obj, folder_path):
    if folder_path == obj.FolderPath:
        return obj

    obj_depth = len(obj.FolderPath.split('\\'))
    folder_path_ary = folder_path.split('\\')
    for folder in obj.Folders:
        obj_folder_path_ary = folder.FolderPath.split('\\')
        if folder_path_ary[obj_depth] == obj_folder_path_ary[-1]:
            return get_folder_by_path(folder, folder_path)


def read_hdr(request_body):
    # print request_body
    trainer = re.search('Created by:\s*([a-zA-Z]+ [a-zA-Z]+)\s', request_body)
    cache = re.search('to be set up:(.+?)\n+', request_body)
    start = re.search('Start date of class:(.+?)\n+', request_body)
    end = re.search('End date of class:(.+?)\n+?', request_body)
    if cache and start and end:
        return ''.join(c for c in cache.group(1) if c.isdigit()), \
               start.group(1).strip(), \
               end.group(1).strip(), \
               trainer.group(1).strip()

    return None, None, None, None


def schedule_class():
    hdr_requests = find_requests()
    print "New Helpdesk Requests found:"
    for hdr in hdr_requests:
        # print hdr
        if all(elm for elm in hdr):
            cache = hdr[0]
            start = format_time(hdr[1])
            end = format_time(hdr[2])
            trainer = hdr[3]
            if int(cache) <= 300 and all(date is not None for date in [start, end]):
                print "\t", cache, start, end, trainer
                MyTrack.save_schedule(cache, start, end, trainer)


def format_time(time_string):
    time_format = "%m/%d/%Y"  # MM/DD/YYYY

    try:
        time_tuple = datetime.datetime.strptime(time_string, time_format)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%m/%d/%y")  # MM/DD/YY
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%d-%m-%Y")  # DD-MM-YYYY
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%m/%d")  # MM/DD
        time_tuple = time_tuple.replace(year=datetime.datetime.now().year)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%a %m/%d")  # WD MM/DD
        time_tuple = time_tuple.replace(year=datetime.datetime.now().year)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%A %m/%d")  # Weekday MM/DD
        time_tuple = time_tuple.replace(year=datetime.datetime.now().year)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%B %d")  # Month DD
        time_tuple = time_tuple.replace(year=datetime.datetime.now().year)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    try:
        time_tuple = datetime.datetime.strptime(time_string, "%b %d")  # M DD
        time_tuple = time_tuple.replace(year=datetime.datetime.now().year)
        return time_tuple.strftime(time_format)
    except ValueError:
        pass

    epic_time = re.search("(^[tTwW])\s*([\-+]*)\s*([0-9]*)$", time_string.strip())
    if epic_time:
        unit_string = epic_time.group(1).upper()
        operator = epic_time.group(2)
        amount_change = epic_time.group(3)
        # print unit_string, operator, amount_change

        if unit_string == "T":
            time_unit = "days"
        elif unit_string == "W":
            time_unit = "weeks"

        if operator and amount_change:
            operator_string = '%s datetime.timedelta(%s=%s)' % (operator, time_unit, amount_change)
        else:
            operator_string = ""

        exec_string = 'time_tuple = datetime.datetime.now() %s' % operator_string

        exec exec_string
        return time_tuple.strftime(time_format)


def send_email(e_address, env):
    outlook = win32com.client.gencache.EnsureDispatch("Outlook.Application")

    # https://msdn.microsoft.com/en-us/library/office/ff869291.aspx
    msg = outlook.CreateItem(win32com.client.constants.olMailItem)
    msg.To = e_address
    msg.Subject = "epic-trn%s Setup Notification" % env
    msg.Body = "epic-trn%s has been setup for your class today" % env
    # msg.Display()
    msg.Send()
    return

# # # #


if __name__ == "__main__":
    # print format_time("w+12")
    schedule_class()
