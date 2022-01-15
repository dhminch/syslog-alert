
import pprint
import re

from Alarm import Alarm
import debug

RE_ENTRY_FIELDS = re.compile(r"(.{15}) ([^:]+) ([^\s:]+?)(?:\[(\d+)\])?: (.*)")
RE_SUDO_MESSAGE_FIELDS = re.compile(r"(\S+) : TTY=(.*) ; PWD=(.*); USER=(.*) ; COMMAND=(.*)")
RE_PKEXEC_MESSAGE_FIELDS = re.compile(r"(\S+): Executing command \[USER=(.*)\] \[TTY=(.*)\] \[CWD=(.*)\] \[COMMAND=(.*)\]")
RE_SSH_LOGIN_MESSAGE_FIELDS = re.compile(r"Accepted (\S+) for (\S+) from ([0-9.]+) port ([0-9]{1,5}) (.+)")
RE_PFSENSE_WEB_LOGIN_MESSAGE_FIELDS = re.compile(r".* Successful login for user '(\S+)' from: ([0-9.]+)")
RE_ESXI_WEB_LOGIN = re.compile(r".*Event 671 : User (\S+)@([0-9.]+) logged in as (.*)")
RE_TTY_LOGIN = re.compile(r"LOGIN ON (\S+) BY (\S+)")

RE_IGNORE_ENTRIES = [
    re.compile(r"org.gnome.Terminal.desktop.*(watch_established|watch_fast|unwatch_fast)"),
    "openmediavault-update-smart-driv Updating smartmontools drive database",
    "/usr/lib/gdm3/gdm-x-session[",
    "gnome-keyring-ssh.desktop[",
    "gnome-keyring-secrets.desktop",
    "libcanberra-login-sound.desktop[ Failed to play sound: File or data not found",
    "org.freedesktop.thumbnails.Thumb Registered thumbnailer",
]

def get_entry_fields(entry):
    match = RE_ENTRY_FIELDS.match(entry)
    if match is None:
        return None
    
    fields = {}
    fields["date"] = match.group(1)
    fields["host"] = match.group(2)
    fields["process"] = match.group(3)
    fields["pid"] = match.group(4)
    fields["message"] = match.group(5).strip()
    return fields

def ignore_entry(entry):
    for pattern in RE_IGNORE_ENTRIES:
        if isinstance(pattern, re.Pattern) and pattern.search(entry):
            return True
        elif isinstance(pattern, str) and pattern in entry:
            return True
    return False

def entry_processor_sudo(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "sudo":
        return None

    match = RE_SUDO_MESSAGE_FIELDS.match(fields["message"])
    if match is None:
        return None

    fields["requesting_user"] = match.group(1)
    fields["tty"] = match.group(2)
    fields["pwd"] = match.group(3)
    fields["target_user"] = match.group(4)
    fields["command"] = match.group(5)

    return Alarm("{}: User {} used sudo on {} to {} as {}".format(
                fields["date"], fields["requesting_user"], fields["host"],
                fields["command"], fields["target_user"]))

def entry_processor_pkexec(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "pkexec":
        return None

    match = RE_PKEXEC_MESSAGE_FIELDS.match(fields["message"])
    if match is None:
        return None

    fields["requesting_user"] = match.group(1)
    fields["target_user"] = match.group(2)
    fields["tty"] = match.group(3)
    fields["pwd"] = match.group(4)
    fields["command"] = match.group(5)

    return Alarm("{}: User {} used pkexec on {} to {} as {}".format(
                fields["date"], fields["requesting_user"], fields["host"],
                fields["command"], fields["target_user"]))

def entry_processor_ssh_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "sshd":
        return None

    match = RE_SSH_LOGIN_MESSAGE_FIELDS.match(fields["message"])
    if match is None:
        return None

    fields["auth_method"] = match.group(1)
    fields["user"] = match.group(2)
    fields["source_ip"] = match.group(3)
    fields["source_port"] = match.group(4)
    fields["ssh_info"] = match.group(5)

    return Alarm("{}: User {} logged into {} via SSH from {} using {}".format(
                fields["date"], fields["user"], fields["host"],
                fields["source_ip"], fields["auth_method"]))

def entry_processor_pfsense_web_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "php-fpm":
        return None

    match = RE_PFSENSE_WEB_LOGIN_MESSAGE_FIELDS.match(fields["message"])
    if match is None:
        return None

    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)

    return Alarm("{}: User {} logged into {} web GUI from {}".format(
                fields["date"], fields["user"], fields["host"],
                fields["source_ip"]))

def entry_processor_esxi_web_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "Hostd":
        return None

    match = RE_ESXI_WEB_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)
    fields["user_agent"] = match.group(3)

    return Alarm("{}: User {} logged into {} ESXi web UI from {} via {}".format(
                fields["date"], fields["user"], fields["host"],
                fields["source_ip"], fields["user_agent"]))

def entry_processor_tty_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_TTY_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["tty"] = match.group(1)
    fields["user"] = match.group(2)

    return Alarm("{}: User {} logged into {} locally via {}".format(
                fields["date"], fields["user"], fields["host"],
                fields["tty"]))