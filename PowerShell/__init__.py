import subprocess
import os

from WebApplication import WebApplication
import Log

PS_PATH = os.path.dirname(os.path.realpath(__file__))
LOGGER = Log.MyLog(name=__name__)


def setup(interconnect, cache):
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Setup-Environment.ps1',
                          '-interconnect', interconnect,
                          '-cache', cache],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        with open(os.path.join(PS_PATH, "setup.err"), 'r') as err:
            err_msg = err.read().decode("utf16").strip()  # can't decode byte 0xff
        log_error("Failed to setup Interconnect-train%s with epic-trn%s: %s" % (interconnect, cache, err_msg))
        return False
    LOGGER.info("Interconnect-train%s connected to epic-trn%s" % (interconnect, cache))
    return True


def cleanup(interconnect, cache):
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Cleanup-Environment.ps1',
                          '-interconnect', interconnect,
                          '-cache', cache],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        log_error("Failed to stop Interconnect-train%s service and remove Interconnect-train%s IIS directory"
                  % (interconnect, cache))
        return False
    LOGGER.info("Interconnect-train%s stopped and removed" % interconnect)
    return True


def get_webapplications():
    web_applications = list()
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Get-WebApplications.ps1'],
                         cwd=PS_PATH,
                         stdout=subprocess.PIPE)
    ps_stdout = p.stdout.read()
    for ps_out in ps_stdout.split("# # # #"):
        if ps_out.strip():
            web_app = WebApplication(ps_out)
            LOGGER.info("WebApplication found for %s" % web_app)
            web_applications.append(web_app)
    if not ps_stdout:
        log_error("Unable to retrieve IIS Web Applications from Interconnect server")
        return False
    return web_applications


def update_app_pools():
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Update-AppPools.ps1'],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        log_error("Unable to update Interconnect Application Pools")
        return False
    LOGGER.info("App Pools for Interconnects updated")
    return True


def restart_services():
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Restart-Services.ps1'],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        log_error("Unable to restart Interconnect-train* services")
        return False
    LOGGER.info("Interconnect-train* services restarted")
    return True


def stop_services():
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Stop-Services.ps1'],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        log_error("Unable to stop Interconnect-train* services")
        return False
    LOGGER.info("Interconnect-train* services stopped")
    return True


def restart_phonebook():
    p = subprocess.Popen([r'powershell.exe',
                          '-ExecutionPolicy', 'Unrestricted',
                          r'.\Restart-TrainingPhonebook.ps1'],
                         cwd=PS_PATH)
    result = p.wait()
    if int(result) != 0:
        log_error("Training Phonebook service not restarted")
        return False
    LOGGER.info("Training Phonebook service restarted")
    return True


def log_error(msg):
    LOGGER.error(msg)

# # # #


if __name__ == "__main__":
    print PS_PATH
