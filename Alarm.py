
from twilio.rest import Client

import debug

class Alarm:

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message[0:160]

class AlarmDispatcher:

    def __init__(self):
        self.alarm_queue = []
        self.alarm_sent = []
        self.alarm_ignored = []

    def load_alarms(self, alarms):
        self.alarm_queue.extend(alarms)

    def send_alarms(self, config):
        client = Client(config.twilio_account_sid, config.twilio_auth_token)

        for alarm in self.alarm_queue:
            debug.log("Dispatching alarm: {}".format(alarm))
            """message = client.messages.create(  
                                    messaging_service_sid=twilio_messagingservice_sid, 
                                    body=msg,      
                                    to=phone
                                )
            print(message.sid)"""
            self.alarm_sent.append(alarm)
        
        self.alarm_queue.clear()

        
    