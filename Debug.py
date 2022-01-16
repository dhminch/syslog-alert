
from datetime import datetime

class Debug:
    verbosity = 1
    output_file = None

    def set_verbosity(level):
        Debug.verbosity = level

    def set_output_file(file):
        if Debug.output_file is not None:
            Debug.output_file.close()
        Debug.output_file = open(file, "a", encoding="utf-8")

    def error(msg):
        if Debug.verbosity >= 1:
            log_msg = "[E] {}: {}".format(datetime.now(), msg)
            print(log_msg)
            Debug.output_file.write(log_msg)

    def log(msg):
        if Debug.verbosity >= 2:
            log_msg = "[L] {}: {}".format(datetime.now(), msg)
            print(log_msg)
            Debug.output_file.write(log_msg)

    def debug(msg):
        if Debug.verbosity >= 3:
            log_msg = "[D] {}: {}".format(datetime.now(), msg)
            print(log_msg)
            Debug.output_file.write(log_msg)
