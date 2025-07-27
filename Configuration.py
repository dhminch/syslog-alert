
import json
import os
import os.path

from Debug import Debug

class Configuration:

    def __init__(self, file):
        if not os.path.isfile(file):
            Debug.error("Configuration file {} does not exist!".format(file))
            exit(1)
        if not os.access(file, os.O_RDONLY):
            Debug.error("Configuration file {} is not readable!".format(file))
            exit(1)

        with open(file, "r", encoding="utf-8") as handle:
            try:
                config_obj = json.load(handle)
            except Exception as e:
                Debug.error("Configuration file {} is not valid JSON!".format(file))
                raise e
            
        self.logs = config_obj["logs"]
        self.monitor_frequency = config_obj["monitor_frequency"]
        self.limits_host_cooldown = config_obj["limits"]["host_cooldown"]
        self.limits_max_per_hour = config_obj["limits"]["max_per_hour"]
        self.limits_max_per_day = config_obj["limits"]["max_per_day"]
        self.pushover_app_token = config_obj["pushover"]["app_token"]
        self.pushover_target_token = config_obj["pushover"]["target_token"]
        self.pushover_disabled = config_obj["pushover"]["disabled"]
        self.logging_verbosity = config_obj["logging_verbosity"]