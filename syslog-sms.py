
import os.path
from signal import signal, SIGINT

from Alarm import AlarmDispatcher
from Configuration import Configuration
from Debug import Debug
from LogMonitor import LogMonitor

def sigint_handler(signal_received, frame):
    print("Exiting now!")
    exit(0)

def main():
    signal(SIGINT, sigint_handler)
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = Configuration(os.path.join(__location__, "config.json"))
    Debug.set_verbosity(config.logging_verbosity, config.logging_file)
    dispatcher = AlarmDispatcher(config)
    logmonitor = LogMonitor(config, dispatcher)
    logmonitor.monitor()

if __name__ == "__main__":
    main()