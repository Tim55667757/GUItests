# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.
# Version: 1.1

# This is runner for test-suites. Please, set all params for tests in config.py and put other libraries into steps_Lib.
# All test-cases and it's sequence realized in test-suite class or difference test-case files.
# This script manages multithread runs of test-suites.


# Importing config file:
import config

# Importing steps-library file with all resources that are need to us:
import steps_lib

# Imports all test-suites file which we have to run:
from test_suite import GUITestSuite


def Main():
    """
    Multithread run list for all test-suites.
    """
    try:
        steps_lib.LOGGER.info('===== Starting %d thread(s) of test-suite =====' % config.testSuiteThreads)

        for i in range(config.testSuiteThreads):
            # Init reports:
            steps_lib.reportExceptions.append({'total': 0, 'TimeoutException': 0, 'NoSuchElementException': 0})
            steps_lib.reportTestSuiteData.append({'timeStart': '0', 'timeStop': '0', 'duration': '0', 'testStatus': 'FAIL'})

            steps_lib.LOGGER.debug('Thread #%d, trying to init next instance of test-suite.' % i)
            steps_lib.threads.append({'thread': steps_lib.threading.Thread(
                                          target=GUITestSuite,
                                          args=(config.URL, config.suiteLogin, config.suitePassword,
                                                config.testSuiteOpTimeout, config.selBrowserString,
                                                steps_lib.workDir + '/' + config.selFFProfile, i)),
                                      'sTime': steps_lib.datetime.now()})
            steps_lib.LOGGER.debug('Thread #%d, new instance of test-suite add to thread list - oK' % i)

            steps_lib.LOGGER.debug('Thread #%d, trying to start test-suite in this thread.' % i)
            steps_lib.threads[i]['thread'].start()
            steps_lib.LOGGER.debug('Thread #%d, test-suite in thread started - oK' % i)

            if (config.testSuiteThreads > 1) and (config.testSuiteRumpUp > 0):
                steps_lib.LOGGER.debug('Pause until start next thread...')
                steps_lib.time.sleep(config.testSuiteRumpUp / config.testSuiteThreads)

        # We're achive given power:
        timeWhenAchiveGivenPower = steps_lib.datetime.now()
        steps_lib.LOGGER.info('All %d test-suite run in separate thread. We are achive given power at %s.' % (config.testSuiteThreads, steps_lib.FormatTimeString(timeWhenAchiveGivenPower)))
        timeDelta = timeWhenAchiveGivenPower + steps_lib.timedelta(0, config.timeToStopTests)

        # Waiting until all threads done or until test-time <= config.timeToStopTests
        threadsAreInProgress = True
        while threadsAreInProgress:
            steps_lib.time.sleep(1)
            for t in steps_lib.threads:
                if t['thread']:
                    if config.repeatCaseSequence:
                        if steps_lib.datetime.now() > timeDelta or config.timeToStopTests <= 0:
                            config.repeatCaseSequence = False
                    threadsAreInProgress = True
                    break
                else:
                    threadsAreInProgress = False
                    config.repeatCaseSequence = False

    except BaseException:
        config.repeatCaseSequence = False
        for t in steps_lib.threads:
            if t['thread']:
                t['thread']._stop()
                t['thread'] = None
        for b in range(len(steps_lib.browsers)):
            steps_lib.CloseBrowser(b)
        steps_lib.LOGGER.error('It were errors while running test-suite in thread!')
        steps_lib.LOGGER.exception('Python exception: ')
        steps_lib.sys.exit(1)

    finally:
        steps_lib.Cleaner()

    steps_lib.sys.exit(0)


# Run this script if you want to running multi-instance of TestSuite for perfomance testing.
if __name__ == "__main__":
    args = steps_lib.ParseArgs()
    if args.sortThreads != None:
        if args.sortThreads == 'default':
            print('Parse default log-file to separate files by threads...')
            steps_lib.LoggerParserByThreads(os.path.join(steps_lib.resultPath, config.stestSuitesLogFile), config.testSuiteThreads)
        elif os.path.exists(args.sortThreads):
            print('Parse your log-file to separate files by threads...')
            steps_lib.LoggerParserByThreads(args.sortThreads, config.testSuiteThreads)
        else:
            print('Your file non-exist.')
    else:
        Main()