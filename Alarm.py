
from enum import Enum
import time
from twilio.rest import Client

from Debug import Debug

class Alarm:

    def __init__(self, host, message):
        self.host = host
        self.message = message
        self.status = AlarmStatus.UNSENT
        self.time_sent = 0

    def __str__(self):
        return self.message[0:160]

class AlarmStatus(Enum):
    UNSENT = 1
    SENT = 2
    IGNORED_HOST_COOLDOWN = 3
    IGNORED_HOUR_LIMIT = 4
    IGNORED_DAY_LIMIT = 5

class AlarmDispatcher:

    def __init__(self, config):
        self.alarm_queue = []
        self.alarm_sent = []
        self.alarm_ignored = []
        self.config = config
        self.client = Client(config.twilio_account_sid, config.twilio_auth_token)

    def load_alarms(self, alarms):
        self.alarm_queue.extend(alarms)

    def send_alarms(self):
        for alarm in self.alarm_queue:
            Debug.log("Dispatching alarm: {}".format(alarm))

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

            Debug.log("Alarm passed rate limit checks, actually sending")
            alarm.time_sent = current_time
            """message = client.messages.create(  
                                    messaging_service_sid=twilio_messagingservice_sid, 
                                    body=msg,      
                                    to=phone
                                )
            print(message.sid)"""
            self.alarm_sent.append(alarm)
        
        self.alarm_queue.clear()
