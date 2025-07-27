
from enum import Enum
import time
import requests

from Debug import Debug

PUSHOVER_MESSAGES_ENDPOINT = 'https://api.pushover.net/1/messages.json'

class Alarm:

    def __init__(self, host, title, message, source):
        self.host = host
        self.title = title
        self.message = message
        self.source = source
        self.status = AlarmStatus.UNSENT
        self.time_created = time.time()
        self.time_sent = 0

    def __str__(self):
        return f"{self.title} - {self.message[0:80]}"

class AlarmStatus(Enum):
    UNSENT = 1
    SENT = 2
    IGNORED_HOST_COOLDOWN = 3
    IGNORED_HOUR_LIMIT = 4
    IGNORED_DAY_LIMIT = 5
    IGNORED_OPENVPN = 6

class AlarmDispatcher:

    def __init__(self, config):
        self.alarm_queue = []
        self.alarm_sent = []
        self.alarm_ignored = []
        self.config = config

    def load_alarms(self, alarms):
        self.alarm_queue.extend(alarms)

    def send_alarms(self):
        for alarm in self.alarm_queue:
            Debug.log("Dispatching alarm: {}".format(alarm.replace('\n', ' ')))

            current_time = time.time()

            alarms_for_host = list(filter(lambda a: a.host == alarm.host, self.alarm_sent))
            if len(alarms_for_host) > 0 and current_time - alarms_for_host[-1].time_sent < self.config.limits_host_cooldown:
                alarm.status = AlarmStatus.IGNORED_HOST_COOLDOWN
                self.alarm_ignored.append(alarm)
                Debug.log("Ignoring alarm due to host cooldown")
                continue

            num_alarms_sent_past_hour =  len(list(filter(lambda a: current_time - a.time_sent < 3600 , self.alarm_sent)))
            if num_alarms_sent_past_hour >= self.config.limits_max_per_hour:
                alarm.status = AlarmStatus.IGNORED_HOUR_LIMIT
                self.alarm_ignored.append(alarm)
                Debug.log("Ignoring alarm due to hour limit reached")
                continue

            num_alarms_sent_past_day =  len(list(filter(lambda a: current_time - a.time_sent < 86400 , self.alarm_sent)))
            if num_alarms_sent_past_day >= self.config.limits_max_per_day:
                alarm.status = AlarmStatus.IGNORED_DAY_LIMIT
                self.alarm_ignored.append(alarm)
                Debug.log("Ignoring alarm due to daily limit reached")
                continue

            # OpenVPN re-authenticates every hour for each user, ignore repeated messages for each user
            if alarm.source == "OPENVPN":
                i = alarm.message.find("User")
                if i > 0:
                    message = alarm.message[i:]
                    if(len(list(filter(lambda a: current_time - a.time_sent < 3600*2, 
                        self.alarm_sent + self.alarm_ignored))) > 0):
                        
                        alarm.status = AlarmStatus.IGNORED_OPENVPN
                        self.alarm_ignored.append(alarm)
                        Debug.log("Ignoring alarm due to repeat OpenVPN messages")
                        continue
            
            alarm.time_sent = current_time
            if self.config.pushover_disabled:
                Debug.log("Alarm would be sent, but Pushover is disabled in the configuration")
            else:
                Debug.log("Sending alarm via Pushover")
                try:
                    response = requests.post(PUSHOVER_MESSAGES_ENDPOINT, 
                        data={
                            'token': self.config.pushover_app_token,
                            'user': self.config.pushover_target_token,
                            'title': alarm.title,
                            'message': alarm.message
                        })
                    response.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    Debug.error("Issue to sending alarm via Pushover: {}".format(e))
            self.alarm_sent.append(alarm)
        
        self.alarm_queue.clear()
