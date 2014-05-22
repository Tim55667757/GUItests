# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.

# This is file with another one functional test-case.


# Importing config file.

try:
    # Importing config file.
    import config
    # Importing steps-library file with all resources that are need to us.
    import steps_lib
except ImportError:
    import sys, os
    FILEPATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append("/".join(FILEPATH.split('/')[:-2]))
    import config
    import steps_lib


def TestCase2(startURL, login, password, opTimeout=5000, browserString='*firefox', ffProfile=None, instance=0):
    """
    Scenario 2
    """
    currentFuncName = steps_lib.sys._getframe().f_code.co_name  # get current function name for message templates
    try:
        startOperation = steps_lib.datetime.now()
        steps_lib.LOGGER.info('Thread #%d, %s, start time: %s' %
                              (instance, currentFuncName, steps_lib.FormatTimeString(startOperation)))

        # ----- Commands and steps for realize this test-case are here:
        status = 0
        # Step 0. Log in.
        status += steps_lib.OpenProjectAndLogin(startURL, login, password, opTimeout, browserString, ffProfile, instance)
        # Step 1. Check Search Page.
        status += steps_lib.CheckSearchPage(opTimeout, instance)

        # ----- Return results and status
        finishOperation = steps_lib.datetime.now()
        steps_lib.LOGGER.info('Thread #%d, %s, finish time: %s' % (instance, currentFuncName, steps_lib.FormatTimeString(finishOperation)))
        steps_lib.LOGGER.info('Thread #%d, %s, duration: %s' % (instance, currentFuncName, str(finishOperation - startOperation)))
        steps_lib.reportTestCaseData.append({'thread': instance,
                                             'timeStart': str(startOperation), 'timeStop': str(finishOperation),
                                             'duration': str(finishOperation - startOperation), 'testStatus': status})
        if status == 0:
            steps_lib.LOGGER.warning('Thread #%d, %s, status code (0): PASS' % (instance, currentFuncName))
        else:
            steps_lib.LOGGER.warning('Thread #%d, %s, status code (%d): FAIL' % (instance, currentFuncName, status))
        if __name__ == "__main__":
            # close browser and kill thread, if we run single test.
            status += steps_lib.CloseBrowser(instance)
            steps_lib.threads[instance]['thread'] = None
        return status
    except Exception:
        steps_lib.LOGGER.error('Thread #%d, %s, status: error' % (instance, currentFuncName))
        steps_lib.LOGGER.exception('Python exception: ')
        return 1



def Main():
    """
    Running only one thread with TestCase2.
    """
    try:
        steps_lib.LOGGER.info('Thread #0, ===== Starting only one thread of test-case TestCase2 =====')

        steps_lib.LOGGER.debug('Thread #0, trying to add next instance of test-case to the thread list.')
        steps_lib.threads.append({'thread': steps_lib.threading.Thread(
                                      target=TestCase2,
                                      args=(config.URL, config.suiteLogin, config.suitePassword,
                                            config.testSuiteOpTimeout, config.selBrowserString,
                                            steps_lib.workDir + '/' + config.selFFProfile, 0)),
                                  'sTime': steps_lib.datetime.now()})
        steps_lib.LOGGER.debug('Thread #0, new instance of test-case add to thread list - oK')

        # Open browser, because this step usually run in test-suite.
        steps_lib.OpenBrowser(config.testSuiteOpTimeout, config.selBrowserString, config.selFFProfile, 0)

        steps_lib.LOGGER.debug('Thread #0, trying to start test-case in this thread.')
        steps_lib.threads[0]['thread'].start()
        steps_lib.LOGGER.debug('Thread #0, test-case in thread started - oK')

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


# Run this script if you want to running only one instance of test-case.
if __name__ == "__main__":
    steps_lib.ParseArgs()
    Main()
