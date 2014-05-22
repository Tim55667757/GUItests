# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.

# This is configuration file for test-runner in tester.py.
# Please, don't rename variable's name! But you may create and add your own variables.


# Base URL for web-project:
URL = 'https://google.ru'

# Credentials for testing. '' by default.
suiteLogin = ''
suitePassword = ''

# Test-case sequence for main test-suite. Specified tests should be exist!
testSuitesCaseSequence = [1, 2]

# Flag to repeat sequence of test-cases. True if you want repeat sequence, False in another case.
repeatCaseSequence = False

# How many threads of test suites do you need?
testSuiteThreads = 2

# Rump up period shows time (sec.) in which all test suite threads will start:
testSuiteRumpUp = 3

# Time in seconds to finish stress tests, after all virtual users up, number <= 0 to infinite loop:
timeToStopTests = 1 * 60

# Operation's timeout in seconds for difficult operations:
testSuiteOpTimeout = 5

# Selenium Browser string. This param shows Selenium WebDriver which browser to run: *firefox, *chrome, *ie
selBrowserString = '*chrome'

# Mozilla profile. This param used only for ff. This is relative path to dir with mozilla profile config.
selFFProfile = 'ff_profile'

# Relative path from directory where test has been started, to the log file's directory.
testSuiteReportDir = 'reports'

# Relative path from report directory to the screenshot file's directory.
testSuiteScreensDir = 'screens'

# Name of log-file for all test-suites.
testSuitesLogFile = 'Test_suites_Log.txt'

# Info level for logger: CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0
loggerInfoLevel = 10

# Name of summary file with report for suite.
testSuiteSummaryFile = 'Test_suite_Summary.txt'

# True if you want to take screenshot on errors, False in another case.
takeScreensOnError = True

# True if you want to take screenshot on every operation (test-steps, not errors), False in another case.
takeScreensOnSteps = True