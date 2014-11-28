#!/usr/bin/env python

import os, sys, time, logging, getopt, glob

from datetime import datetime
from subprocess import call, Popen

from daemon import Daemon

FLIGHT = None
BASEPATH = os.path.dirname(os.path.abspath(__file__))
DAEMON_PATH = "{}/pid".format(BASEPATH)
if not os.path.exists(DAEMON_PATH):
    os.makedirs(DAEMON_PATH)
LOGGING_PATH = "{}/log".format(BASEPATH)
if not os.path.exists(LOGGING_PATH):
    os.makedirs(LOGGING_PATH)

SLEEPING_TIME = 3600

class FlightDaemon(Daemon):
    def startup(self):
        global LOGGING_PATH, FLIGHT

        FORMAT = "[%(asctime)-15s] [%(levelname)-s] - %(message)s"

        logging_file = "{}/{}.log".format(LOGGING_PATH, FLIGHT.lower())
        logging.basicConfig(format=FORMAT, filename=logging_file, level=logging.INFO)

    def run(self):
        global BASEPATH, FLIGHT, SLEEPING_TIME, LOGGING_PATH

        pre_current_date = None
        while True:
            current_date = datetime.today().strftime("%Y-%m-%d")
            if pre_current_date == None or pre_current_date != current_date:
                # Move to the working directory
                working_directory = "{}/{}".format(BASEPATH, FLIGHT)
                
                os.chdir(working_directory)
                logging.info("Change the working directory to {}".format(working_directory))

                logging.info("Start to crawl task for {}".format(FLIGHT))
                for from_city in glob.glob("fromCity*cfg"):
                    for to_city in glob.glob("toCity*cfg"):
                        commend = "sh {}.sh {} {}".format(FLIGHT.lower(), from_city, to_city)
                        logging.info("The commend is {}".format(commend))

                        call(commend, shell=True)

                logging.info("End of crawling task")
            else:
                logging.info("Skip this crawling task")

            pre_current_date = current_date
            time.sleep(SLEEPING_TIME)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:a:")
    except getopt.GetoptError as err:
        print str(err) # will print something like "option -a not recognized"
        sys.exit(2)

    action = None
    for o, a in opts:
        if o == "-p":
            FLIGHT = a
        elif o == "-a":
            action = a.lower()

    daemon = FlightDaemon('{}/daemon-{}.pid'.format(DAEMON_PATH, FLIGHT))
    if 'start' == action:
        daemon.start()
    elif 'stop' == action:
        daemon.stop()
    elif 'restart' == action:
        daemon.restart()
    else:
        print "Unknown command"
        sys.exit(2)

    sys.exit(0)
