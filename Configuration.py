
from distutils.command.config import config
import json
import os
import os.path

import debug

class Configuration:

    def __init__(self, file):
        if not os.path.isfile(file):
            debug.log("Configuration file {} does not exist!".format(file))
            exit(1)
        if not os.access(file, os.O_RDONLY):
            debug.log("Configuration file {} is not readable!".format(file))
            exit(1)

        with open(file, "r", encoding="utf-8") as handle:
            try:
                config_obj = json.load(handle)
            except Exception as e:
                debug.log("Configuration file {} is not valid JSON!".format(file))
                raise e
            
        self.logs = config_obj["logs"]
        self.cellphone = config_obj["cellphone"]
        self.limits_host_cooldown = config_obj["limits"]["host_cooldown"]
        self.limits_max_per_hour = config_obj["limits"]["max_per_hour"]
        self.limits_max_per_day = config_obj["limits"]["max_per_day"]
        self.twilio_messagingservice_sid = config_obj["twilio"]["messagingservice_sid"]
        self.twilio_account_sid = config_obj["twilio"]["account_sid"]
        self.twilio_auth_token = config_obj["twilio"]["auth_token"]