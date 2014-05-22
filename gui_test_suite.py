# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.

# This file can be use for creates test-suite with list of functional test-cases. Test-cases are in the "tests" directory.


# Importing config file:
import config

# Importing steps-library file with all resources that are need to us:
import steps_lib

# Importing all test-cases from test directories which you want to run:
from tests.test_case_1_Init_test import TestCase1
from tests.test_case_2_Search_test import TestCase2


# You must specify test to run in next test-suite:
def GUITestSuite(startURL, login, password, opTimeout=5000, browserString='*firefox', ffProfile='ff_profile', instance=0):
    """
    This function defines which test-cases will be run in this test-suite.
    """
    steps_lib.LOGGER.info('Thread #%s, --- Start test-suite ---' % str(instance))
    startOperation = steps_lib.datetime.now()
    steps_lib.LOGGER.info('Thread #%s, test-suite start time: %s' % (str(instance), steps_lib.FormatTimeString(startOperation)))

    # ----- Test-cases and steps which you want to run are here:
    status = 0
    flagToRepeat = True

    # Open browser first:
    status += steps_lib.OpenBrowser(opTimeout, browserString, ffProfile, instance)

    while flagToRepeat:
        status = 0
        # ----- run all cases specify in global Case Sequence:
        for case in config.testSuitesCaseSequence:

            if case == 1:
                status += TestCase1(startURL, login, password, opTimeout, browserString, ffProfile, instance)

            elif case == 2:
                status += TestCase2(startURL, login, password, opTimeout, browserString, ffProfile, instance)

            else:
                steps_lib.LOGGER.error('Thread #%s, incorrect test id in test-case\'s sequence! Stop.' % str(instance))
                config.repeatCaseSequence = False

        if config.repeatCaseSequence:
            flagToRepeat = True
        else:
            flagToRepeat = False

        # ----- Return results and status:
        if status == 0:
            steps_lib.LOGGER.info('Thread #%s, test-suite status: PASS' % str(instance))
        else:
            steps_lib.LOGGER.info('Thread #%s, test-suite status: FAIL' % str(instance))
        finishOperation = steps_lib.datetime.now()
        steps_lib.LOGGER.info('Thread #%s, test-suite finish time: %s' % (str(instance), steps_lib.FormatTimeString(finishOperation)))
        steps_lib.LOGGER.info('Thread #%s, test-suite duration: %s' % (str(instance), str(finishOperation - startOperation)))

        # Adding info to summary:
        steps_lib.reportTestSuiteData[instance] = {'thread': instance, 'timeStart': str(startOperation),
                                                   'timeStop': str(finishOperation),
                                                   'duration': str(finishOperation - startOperation),
                                                   'testStatus': status}
        steps_lib.reportByThreads.append(steps_lib.reportTestSuiteData[instance])
        fullReportPath = steps_lib.workDir + '/' + config.testSuiteReportDir + '/' + config.testSuiteSummaryFile
        steps_lib.LOGGER.info('Thread #%s, Trying to publish output results of test-suite in summary file: %s' %
                              (str(instance), fullReportPath))
        steps_lib.FormattingReportOutput(fullReportPath)
        steps_lib.LOGGER.info('Thread #%s, Publish summary file, status: oK' % str(instance))
        startOperation = steps_lib.datetime.now()

    # close browser and kill thread:
    status += steps_lib.CloseBrowser(instance)
    steps_lib.threads[instance]['thread'] = None
    return status


def Main():
    """
    Running 1 thread of TestSuite.
    """
    try:
        steps_lib.LOGGER.info('===== Starting 1 thread of test-suite =====')

        # Init reports.
        steps_lib.reportExceptions.append({'all': 0, 'TimeoutException': 0, 'NoSuchElementException': 0})
        steps_lib.reportTestSuiteData.append({'timeStart': '0', 'timeStop': '0', 'duration': '0', 'testStatus': 'FAIL'})

        steps_lib.LOGGER.info('Thread #0, trying to init next instance of test-suite.')
        steps_lib.threads.append({'thread': steps_lib.threading.Thread(
                                      target=GUITestSuite,
                                      args=(config.URL, config.suiteLogin, config.suitePassword,
                                            config.testSuiteOpTimeout, config.selBrowserString,
                                            steps_lib.workDir + '/' + config.selFFProfile, 0)),
                                  'sTime': steps_lib.datetime.now()})
        steps_lib.LOGGER.info('Thread #0, new instance of test-suite add to thread list - oK')

        steps_lib.LOGGER.info('Thread #0, trying to start test-suite in this thread.')
        steps_lib.threads[i]['thread'].start()
        steps_lib.LOGGER.info('Thread #0, test-suite in thread started - oK')

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


# Run this script if you want to run only one instance of test-suite (for functional testing only).
if __name__ == "__main__":
    steps_lib.ParseArgs()
    Main()
