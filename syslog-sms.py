
from twilio.rest import Client

from Configuration import Configuration
import debug
import entry_processors

ENTRY_PROCESSORS = [
    entry_processors.entry_processor_ssh_login,
    entry_processors.entry_processor_sudo,
    entry_processors.entry_processor_pkexec,
    entry_processors.entry_processor_pfsense_web_login,
    entry_processors.entry_processor_esxi_web_login,
    entry_processors.entry_processor_tty_login,
]

def generate_alarm_for_entry(entry):
    alarms = []

    for processor in ENTRY_PROCESSORS:
        debug.debug("Trying processor {}".format(processor.__name__))
        alarm = processor(entry)
        if alarm:
            alarms.append(alarm)

    return alarms

def process_logs(logs):
    alarms = []

    for file in logs:
        debug.log("Processing log file {}".format(file))
        with open(file, "r", encoding='utf-8') as handle:
            for entry in handle:
                entry = entry.strip()
                debug.debug("Processing entry {}".format(entry))
                if entry == "":
                    continue
                if entry_processors.ignore_entry(entry):
                    continue
                alarms.extend(generate_alarm_for_entry(entry))

    return alarms

def process_alarms(alarms):
    pass

def send_alarm(twilio_account_sid, twilio_messagingservice_sid, twilio_auth_token, phone, msg):
    client = Client(twilio_account_sid, twilio_auth_token) 
 
    message = client.messages.create(  
                                messaging_service_sid=twilio_messagingservice_sid, 
                                body=msg,      
                                to=phone
                            )
    print(message.sid)

def main():
    config = Configuration("config.json")
    #send_alarm(config.twilio_account_sid, config.twilio_messagingservice_sid, config.twilio_auth_token, config.cellphone, "Test Message alpha")
    alarms = process_logs(config.logs)
    process_alarms(alarms)

if __name__ == "__main__":
    main()