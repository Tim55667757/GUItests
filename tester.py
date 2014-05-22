# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.

# This is runner for test-suites. Please, set all params for tests in config.py and put other libraries into steps_Lib.
# All test-cases and it's sequence realized in test-suite class or difference test-case files.
# This script manages multithread runs of test-suites.


# Importing config file:
import config

# Importing steps-library file with all resources that are need to us:
import steps_lib

# Imports all test-suites file which we have to run:
from gui_test_suite import GUITestSuite


def Main():
    """
    Multithread run list for all test-suites
    """
    try:
        steps_lib.LOGGER.info('===== Starting %d thread(s) of test-suite =====' % config.testSuiteThreads)

        for i in range(config.testSuiteThreads):
            # Init reports:
            steps_lib.reportExceptions.append({'all': 0, 'TimeoutException': 0, 'NoSuchElementException': 0})
            steps_lib.reportTestSuiteData.append({'timeStart': '0', 'timeStop': '0', 'duration': '0', 'testStatus': 'FAIL'})

            steps_lib.LOGGER.info('Thread #%s, trying to init next instance of test-suite.' % str(i))
            steps_lib.threads.append({'thread': steps_lib.threading.Thread(
                                          target=GUITestSuite,
                                          args=(config.URL, config.suiteLogin, config.suitePassword,
                                                config.testSuiteOpTimeout, config.selBrowserString,
                                                steps_lib.workDir + '/' + config.selFFProfile, i)),
                                      'sTime': steps_lib.datetime.now()})
            steps_lib.LOGGER.info('Thread #%s, new instance of test-suite add to thread list - oK' % str(i))

            steps_lib.LOGGER.info('Thread #%s, trying to start test-suite in this thread.' % str(i))
            steps_lib.threads[i]['thread'].start()
            steps_lib.LOGGER.info('Thread #%s, test-suite in thread started - oK' % str(i))

            if (config.testSuiteThreads > 1) and (config.testSuiteRumpUp > 0):
                steps_lib.LOGGER.info('Pause until start next thread...')
                steps_lib.time.sleep(config.testSuiteRumpUp / config.testSuiteThreads)

        # Waiting until all threads done.
        threadsAreInProgress = True
        while threadsAreInProgress:
            for t in steps_lib.threads:
                if t['thread'] != None:
                    threadsAreInProgress = True
                    break
                else:
                    threadsAreInProgress = False

    except BaseException:
        config.repeatCaseSequence = False
        for t in steps_lib.threads:
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
            steps_lib.LoggerParserByThreads(steps_lib.resultPath + '/' + config.stestSuitesLogFile, config.testSuiteThreads)
        elif os.path.exists(args.sortThreads):
            print('Parse your log-file to separate files by threads...')
            steps_lib.LoggerParserByThreads(args.sortThreads, config.testSuiteThreads)
        else:
            print('Your file non-exist.')
    else:
        Main()