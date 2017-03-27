from flask import session, request
import random
import string
import subprocess
import re

from WebApp import app_logger

CUR_SESSIONS = dict()  # {session_id: IN_USE}
SESSION_IP = dict()  # {session_id: ip_address}


def get_in_use_ip():
    for sid, in_use in CUR_SESSIONS.iteritems():
        if in_use:
            return SESSION_IP[sid]
    return None


def check_in_use():
    sid = get_current_session()
    if True in CUR_SESSIONS.values():
        if CUR_SESSIONS[sid]:  # if you are the one using the app, it's not 'in use'
            return False
        else:
            return True
    else:
        return False


def set_in_use():
    sid = get_current_session()
    app_logger.info("App in use by %s" % SESSION_IP[sid])
    CUR_SESSIONS[sid] = True


def remove_in_use():
    sid = get_current_session()
    app_logger.info("%s done using app" % SESSION_IP[sid])
    CUR_SESSIONS[sid] = False


def get_current_session_ip():
    sid = get_current_session()
    return SESSION_IP[sid]


def get_current_session():
    sid = session.get('id')
    if sid is not None:
        return sid
    else:
        new_sid = _random_string_()
        while new_sid in CUR_SESSIONS:
            new_sid = _random_string_()
        session['id'] = new_sid
        CUR_SESSIONS[new_sid] = False
        SESSION_IP[new_sid] = reverse_ip_lookup(request.remote_addr)
        app_logger.info("New session, %s, for %s" % (new_sid, SESSION_IP[new_sid]))
        return new_sid


def _random_string_(N=16):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))


def reverse_ip_lookup(ip_address):
    p = subprocess.Popen(["ping",
                          "-n", "1",
                          "-a",
                          ip_address],
                         stdout=subprocess.PIPE)
    cmd_stdout = p.stdout.read()
    fqdn = re.search('Pinging\s*(.+?)\s*\[', cmd_stdout)
    if fqdn:
        return fqdn.group(1)
    return ip_address

# # # #


if __name__ == "__main__":
    print reverse_ip_lookup("10.17.7.10")
