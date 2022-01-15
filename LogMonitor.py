
import io
import os
import time

from Debug import Debug
import entry_processors

ENTRY_PROCESSORS = [
    entry_processors.entry_processor_ssh_login,
    entry_processors.entry_processor_sudo,
    entry_processors.entry_processor_pkexec,
    entry_processors.entry_processor_pfsense_web_login,
    entry_processors.entry_processor_esxi_web_login,
    entry_processors.entry_processor_tty_login,
]

class LogMonitor:

    class LogFile:

        def __init__(self, file, handle, inode):
            self.file = file
            self.handle = handle
            self.inode = inode

    def __init__(self, config, dispatcher):
        self.dispatcher = dispatcher
        self.config = config
        self.logs_data = []

    def monitor(self):
        self.init_logs()
        while True:
            Debug.log("Sleeping for {} seconds".format(self.config.monitor_frequency))
            time.sleep(self.config.monitor_frequency)
            self.process_logs()
            self.dispatcher.send_alarms()

    def init_logs(self):
        Debug.log("Initalizing logs")
        for log in self.config.logs:
            Debug.log("Initalizing log file {}".format(log))
            handle = open(log, "r", encoding='utf-8')
            handle.seek(0, io.SEEK_END)
            inode = os.stat(log).st_ino
            logdata = LogMonitor.LogFile(log, handle, inode)
            self.logs_data.append(logdata)

    def check_entry_for_alarms(self, entry):
        alarms = []

        for processor in ENTRY_PROCESSORS:
            Debug.debug("Trying processor {}".format(processor.__name__))
            alarm = processor(entry)
            if alarm:
                alarms.append(alarm)

        return alarms

    def process_logs(self):
        for log_data in self.logs_data:
            Debug.log("Processing log file {}".format(log_data.file))
            self.process_log(log_data.handle)

            inode_on_disk = os.stat(log_data.file).st_ino
            if log_data.inode != inode_on_disk:
                Debug.log("File inode for {} changed from {} to {}, processing file at new inode".format(
                    log_data.file, log_data.inode, inode_on_disk
                ))
                log_data.handle.close()
                log_data.handle = open(log_data.file, "r", encoding='utf-8')
                log_data.inode = inode_on_disk
                self.process_log(log_data.handle)

    def process_log(self, log_handle):
        alarms = []
        for entry in log_handle:
                entry = entry.strip()
                Debug.debug("Processing entry {}".format(entry))
                if entry == "":
                    continue
                if entry_processors.ignore_entry(entry):
                    continue
                alarms.extend(self.check_entry_for_alarms(entry))
        self.dispatcher.load_alarms(alarms)