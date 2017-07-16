"""
Created on Mon July 10, 2017

@author: Ruchika Chhabra
"""

import subprocess
import time
import argparse as cmdline

def argChecks(cmdargs):
    '''
    DESCRIPTION:
    ------------
    Validation check for command line arguments.
    '''
    try:
        assert cmdargs.AnalysisTime != 0, 'AnalysisTime should be specified!'
    except:
        print('Incorrect Arguments passed on command-line!')
        raise

def parseArgs():
    '''
    DESCRIPTION:
    ------------
    Defines command line arguments of Main Module.
    '''
    cmd_parser = cmdline.ArgumentParser(description='Main Module command line arguments.')

    cmd_parser.add_argument('--AnalysisTime', type=int, default=0, \
                            help='Time (in minutes) for which Crawler is \
                                  repeatedly executed at time interval of every 15min.')
    return cmd_parser.parse_args()

def main(cmdargs):
    '''
    DESCRIPTION:
    ------------
    Main function executes:
    1. News Crawler at time interval of 15min for total time represented
       by AnalysisTime option.
    2. News is Crawled from different news sources and inserted to
       elastic search.

    PARAMETERS:
    ----------
    1. cmdargs: command line arguments of Main Module.
    '''
    startTime = time.time()
    while (((time.time() - startTime) / 60) < float(cmdargs.AnalysisTime)):
        # Execute Crawler only for the first time
        proc = subprocess.Popen(['scrapy', 'runspider', '--nolog', 'newsCrawler.py'], shell=True)
        proc.wait()
        if (((time.time() - startTime) / 60) < float(cmdargs.AnalysisTime)):
            print("WAIT FOR 15 MINUTES...")
            time.sleep(900)  # Crawler is executed after 15mins i.e. 900s.

if __name__ == '__main__':
    # Parse command line arguments
    cmdargs = parseArgs()

    # Validation check of command line arguments
    argChecks(cmdargs)

    # Start calling main function now and every 120sec thereafter
    main(cmdargs)