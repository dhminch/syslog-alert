
import pprint
import re

from Alarm import Alarm
from Debug import Debug

RE_ENTRY_FIELDS = re.compile(r"(.{15}) ([^:]+) ([^\s:]+?)(?:\[(\d+)\])?: (.*)")
RE_MINIMAL_ENTRY_FIELDS = re.compile(r"(.{15}) ([^:]+) (.*)")

RE_SUDO_MESSAGE_FIELDS = re.compile(r"(\S+) : TTY=(.*) ; PWD=(.*); USER=(.*) ; COMMAND=(.*)")
RE_PKEXEC_MESSAGE_FIELDS = re.compile(r"(\S+): Executing command \[USER=(.*)\] \[TTY=(.*)\] \[CWD=(.*)\] \[COMMAND=(.*)\]")
RE_SSH_LOGIN_MESSAGE_FIELDS = re.compile(r"Accepted (\S+) for (\S+) from ([0-9.]+) port ([0-9]{1,5}) (.+)")
RE_PFSENSE_WEB_LOGIN_MESSAGE_FIELDS = re.compile(r".* Successful login for user '(\S+)' from: ([0-9.]+)")
RE_ESXI_WEB_LOGIN = re.compile(r".*User (\S+)@([0-9.]+) logged in as (.*)")
RE_TTY_LOGIN = re.compile(r"LOGIN ON (\S+) BY (\S+)")
RE_OPENVPN_LOGIN = re.compile(r"user '(\S+)' authenticated")
RE_WIREGUARD_LOGIN = re.compile(r"WireGuard: New connection - Interface: (\S+), Peer: (\S+), Endpoint: (\S+):(\S+)")
RE_OMV_WEB_LOGIN = re.compile(r"Authorized login from ([a-fA-F0-9:.]+) \[username=(\S+), user-agent=([^\]]+)]")
RE_UNIFI_WEB_LOGIN = re.compile(r"=(\S+) opened UniFi Network via the web. UNIFICategory=System UNIFIsubCategory=Admin Activity admin_ip=([0-9.]+)")
RE_IDRAC_LOGIN = re.compile(r".*USR0030, Message: Successfully logged in using (\S+), from (\S+) and (\S+)")

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
    
# iDRAC uses an entirely different format than standard syslog
# also happens that Unifi web logs work with this too
def get_minimal_entry_fields(entry):
    match = RE_MINIMAL_ENTRY_FIELDS.match(entry)
    if match is None:
        return None
    
    fields = {}
    fields["date"] = match.group(1)
    fields["host"] = match.group(2)
    fields["message"] = match.group(3).strip()
    return fields

def ignore_entry(entry):
    for pattern in RE_IGNORE_ENTRIES:
        if "search" in dir(pattern) and pattern.search(entry):
            return True
        elif isinstance(pattern, str) and pattern in entry:
            return True
    return False

def entry_processor_sudo(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
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
    
    return Alarm(host=fields['host'], 
                title=f"Privileges elevated on {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['requesting_user']}\nHost: {fields['host']}\nMethod: sudo\nCommand: {fields['command']}\nTarget User: {fields['target_user']}",
                source='SUDO')

def entry_processor_pkexec(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
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

    return Alarm(host=fields['host'], 
                title=f"Privileges elevated on {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['requesting_user']}\nHost: {fields['host']}\nMethod: pkexec\nCommand: {fields['command']}\nTarget User: {fields['target_user']}",
                source='SUDO')

def entry_processor_ssh_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
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
                
    return Alarm(host=fields['host'], 
                title=f"Successful SSH login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}\nAuth Method: {fields['auth_method']}",
                source='SSH')

def entry_processor_pfsense_web_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "php-fpm":
        return None

    match = RE_PFSENSE_WEB_LOGIN_MESSAGE_FIELDS.match(fields["message"])
    if match is None:
        return None

    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)

    return Alarm(host=fields['host'], 
                title=f"Successful web login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}",
                source='PFSENSEWEB')

def entry_processor_esxi_web_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    if fields["process"] != "Hostd":
        return None

    match = RE_ESXI_WEB_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)
    fields["user_agent"] = match.group(3)

    return Alarm(host=fields['host'], 
                title=f"Successful web login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}\nUser Agent: {fields['user_agent']}",
                source='ESXIWEB')

def entry_processor_tty_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_TTY_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["tty"] = match.group(1)
    fields["user"] = match.group(2)

    return Alarm(host=fields['host'], 
                title=f"Successful local authentication to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nTTY: {fields['tty']}",
                source='TTYLOGIN')

def entry_processor_openvpn_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_OPENVPN_LOGIN.match(fields["message"])
    if match is None:
        return None

    if fields["process"] != "openvpn":
        return None

    fields["user"] = match.group(1)

    return Alarm(host=fields['host'], 
                title=f"Successful VPN login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nVPN: OpenVPN",
                source='OPENVPN')
                
def entry_processor_wireguard_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_WIREGUARD_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["interface"] = match.group(1)
    fields["peer"] = match.group(2)
    fields["ip"] = match.group(3)
    fields["port"] = match.group(4)

    return Alarm(host=fields['host'], 
                title=f"Successful VPN login to {fields['host']}",
                message=f"{fields['date']}\nPeer: {fields['peer']}\nHost: {fields['host']}\nSource IP: {fields['ip']}\nVPN: Wireguard",
                source='WIREGUARD')

def entry_processor_omv_web_login(entry):
    fields = get_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_OMV_WEB_LOGIN.match(fields["message"])
    if match is None:
        return None

    if fields["process"] != "openmediavault-webgui":
        return None

    fields["source_ip"] = match.group(1)
    fields["user"] = match.group(2)
    fields["user_agent"] = match.group(3)

    return Alarm(host=fields['host'], 
                title=f"Successful web login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}\nUser Agent: {fields['user_agent']}",
                source='OMVWEB')

def entry_processor_unifi_web_login(entry):
    fields = get_minimal_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from entry: {}".format(entry))
        return None

    match = RE_OMV_WEB_LOGIN.match(fields["message"])
    if match is None:
        return None

    if fields["process"] != "openmediavault-webgui":
        return None
        
    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)

    return Alarm(host=fields['host'], 
                title=f"Successful web login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}",
                source='UNIFIWEB')
                
def entry_processor_idrac_login(entry):
    fields = get_minimal_entry_fields(entry)
    if fields is None:
        Debug.log("Unable to parse fields from custom iDRAC entry: {}".format(entry))
        return None

    match = RE_IDRAC_LOGIN.match(fields["message"])
    if match is None:
        return None

    fields["user"] = match.group(1)
    fields["source_ip"] = match.group(2)
    fields["method"] = match.group(3)

    return Alarm(host=fields['host'], 
                title=f"Successful web login to {fields['host']}",
                message=f"{fields['date']}\nUser: {fields['user']}\nHost: {fields['host']}\nSource IP: {fields['source_ip']}\nMethod: {fields['method']}",
                source='IDRAC')
                