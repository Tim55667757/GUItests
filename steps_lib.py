# -*- coding: utf-8 -*-
# Author: Gilmullin T.M.

# This file describes separate logical steps and helper functions.
# These steps are used in various test-cases and test-suites.
# One step is not test-case! But every step-function has result as 0 or 1 too.
# You can use steps for divide your test by logical.
# All imports must be here. In other files you can imports only config.py and steps_lib.py


# Importing Selenium WebDriver classes
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains


# Importing config file:
import config

# Importing LOGGER library:
import logging

# Other imports:
import traceback
import os
import sys
import shutil
from datetime import datetime
import time
import threading
import random
import urllib
import urllib.request
import urllib.parse
import argparse
import subprocess


# Working Directory.
workDir = os.path.abspath(os.curdir)

# Full Path to report directory
resultPath = workDir + '/' + config.testSuiteReportDir

# List of test-suite threads with start time. This is dictionaries: {'thread': <thread>, 'sTime': <start_time>}
threads = []

# List of browsers - one browser in every thread.
browsers = []

# List of dictionaries for test-suite results only. Dict's format:
# {'thread': <thread>, 'timeStart': <start>, 'timeStop': <stop>, 'duration': <stop-start>, 'testStatus': <status>}
reportTestSuiteData = []
reportTestCaseData = []
reportByThreads = []

# List of dictionaries for Exception's statistic by threads. Dict's format:
# {'all': <num>, 'TimeoutException': <num>, 'NoSuchElementException': <num>}
reportExceptions = []


# Settings for LOGGER:
try:
    if not (os.path.exists(resultPath)):
        os.mkdir(resultPath)
    if not (os.path.exists(resultPath + '/logs')):
        os.mkdir(resultPath + '/logs')
    LOGGER = logging.getLogger('Test Logger')
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.FileHandler(resultPath + '/' + config.testSuitesLogFile)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
except Exception:
    print('Can\'t start LOGGER!')
    sys.exit(1)


def Cleaner():
    """
    This function use for finalization operations of test.
    """
    print('Parse default log-file to separate files by threads...')
    LoggerParserByThreads(resultPath + '/' + config.testSuitesLogFile, config.testSuiteThreads)


def StringOfNumToNumsList(string):
    """
    Get some string with numbers and other simbols, for example: '[572,573,604,650]' or similar
    and convert it to list of numbers as [572, 573, 604, 650].
    """
    numList = []
    try:
        while len(string) != 0:
            s = ''
            i = 0
            flag = True
            while flag and i < len(string):
                if string[i] in '0123456789':
                    s = s + string[i]
                    i += 1
                else:
                    flag = False
            if s != '':
                numList.append(int(s))
            string = string[i + 1:]
    except:
        print('Can\'t parse your string of numbers to list of numbers!')
        return []
    return numList


def LoggerParserByThreads(summaryLogFile, threadsNum=1):
    """
    Get summary log file and parse it by separate thread.
    """
    if os.path.exists(summaryLogFile):
        for t in range(threadsNum):
            try:
                logFile = resultPath + '/logs/' + datetime.now().strftime('%d_%m_%Y_%H_%M_%S_') + 'Thread_' + str(t)
                if not (os.path.exists(logFile)):
                    os.mkdir(logFile)
                logFile = logFile + '/Thread_' + str(t)
                if len(reportByThreads) > 0:
                    FormattingReportOutputForCasesByThreadsToCSV(logFile + '_summary.csv', t)
                logFile = logFile + '_all_logs.txt'
                with open(summaryLogFile) as fileFrom:
                    with open(logFile, 'w', encoding='utf-8') as fileTo:
                        summary = fileFrom.readlines()
                        for s in summary:
                            if '#' + str(t) in s:
                                parseString = s
                                fileTo.write(parseString)
            except Exception:
                print('Can\'t parse summary report file %s' % summaryLogFile)
                return 1
    return 0


def FormattingReportOutputForCasesByThreadsToCSV(pathToCaseSummary, threadNum):
    """
    Function create summary report file for cases bt threads.
    """
    try:
        if os.path.exists(pathToCaseSummary):
            file = open(pathToCaseSummary, 'a', encoding='utf-8')
        else:
            file = open(pathToCaseSummary, 'w', encoding='utf-8')
            file.writelines(
                'Thread;timeStart;timeStop;duration;testStatus;all_exceptions;TimeoutException;NoSuchElementException\n')
        for data in reportByThreads:
            if (data['testStatus'] == 0) or (data['testStatus'] == 'PASS'):
                data['testStatus'] = 'PASS'
            else:
                data['testStatus'] = 'FAIL'
        for data in reportByThreads:
            if data['thread'] == threadNum:
                file.writelines('%(thread)d;%(timeStart)s;%(timeStop)s;%(duration)s;%(testStatus)s;' % data +
                                '%(all)d;%(TimeoutException)d;%(NoSuchElementException)d\n' %
                                reportExceptions[threadNum])
        file.close()
    except Exception:
        LOGGER.error('Can not create summary file %s' % fullPath)
        LOGGER.exception('Python exception: ')
        return 1
    return 0


def ParseArgs():
    """
    Function get and parse command line keys.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cases", type=str, help="Set sequence of test-cases, for example: -c [572,573,...]")
    parser.add_argument("-f", "--flagToRepeat", type=str, help="Flag to repeat sequence of test-cases. Type '-f True' for repeat sequence.")
    parser.add_argument("-b", "--browser", type=str, help="Set browser string (*firefox, *chrome, *ie).")
    parser.add_argument("-t", "--threads", type=int, help="Thread's number.")
    parser.add_argument("-r", "--rumpUp", type=int, help="Rump up period shows time (sec.) in which all test suite threads will start.")
    parser.add_argument("-l", "--login", type=str, help="User login.")
    parser.add_argument("-p", "--password", type=str, help="User password.")
    parser.add_argument("-T", "--timeout", type=int, help="Operation's timeout (sec.).")
    parser.add_argument("-u", "--URL", type=str, help="Main project's URL.")
    parser.add_argument("-e", "--takeErrScr", type=str, help="Select this key or type '-e True' if you want to take screenshot on errors.")
    parser.add_argument("-a", "--takeAllScr", type=str, help="Select this key or type '-a True' if you want to take screenshot on every operation.")
    parser.add_argument("-s", "--sortThreads", type=str, help="Type '-s <log-file>' to sort any log-file by threads to log dir. Or '-s default'.")
    args = parser.parse_args()
    if args.cases != None:
        config.testSuitesCaseSequence = StringOfNumToNumsList(args.cases)
    if args.flagToRepeat == 'True':
        config.repeatCaseSequence = True
    else:
        config.repeatCaseSequence = False
    if args.browser != None:
        config.selBrowserString = args.browser
    if args.threads != None:
        config.testSuiteThreads = args.threads
    if args.rumpUp != None:
        config.testSuiteRumpUp = args.rumpUp
    if args.login != None:
        config.suiteLogin = args.login
    if args.password != None:
        config.suitePassword = args.password
    if args.timeout != None:
        config.testSuiteOpTimeout = args.timeout
    if args.URL != None:
        config.URL = args.centerURL
    if (args.takeErrScr == None) or (args.takeErrScr == 'True'):
        config.takeScreensOnError = True
    else:
        config.takeScreensOnError = False
    if (args.takeAllScr == None) or (args.takeAllScr == 'True'):
        config.takeScreensOnSteps = True
    else:
        config.takeScreensOnSteps = False
    return args


def FormatTimeString(timeAndDate):
    """
    Function gets time and date and converts it into Project's log format string
    """
    return timeAndDate.strftime('%H:%M:%S %d.%m.%Y')


def RndTextString(length=5):
    """
    Function outputs random text-string definite length, that will be use for editing fields
    """
    dic = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()-_+='
    textString = ''
    for i in range(length):
        textString = textString + dic[random.randint(0, len(dic) - 1)]
    textString = '[' + textString + ']'
    return textString


def FormattingReportOutput(fullPath):
    """
    Function gets file to summary report. Function create summary report file.
    """
    try:
        file = open(fullPath, 'a', encoding='utf-8')
        file.write('\n  --- Summary Report for Test-suite by threads ---\n')
        file.write('Report date and time: %s \n' % FormatTimeString(datetime.now()))
        file.write('Options for all threads:\n')
        file.write('    - case sequence in test-suite: %s\n' % str(config.testSuitesCaseSequence))
        file.write('    - project\'s URL: %s\n' % str(config.URL))
        file.write('    - browser string: %s\n' % config.selBrowserString)
        file.write('    - operation\'s timeout (sec.): %s\n' % str(config.testSuiteOpTimeout))
        file.write('    - threads of test suite: %s\n' % str(config.testSuiteThreads))
        file.write('    - rump up period (sec.): %s\n' % str(config.testSuiteRumpUp))
        file.write('    - take screens on error: %s\n' % str(config.takeScreensOnError))
        file.write('    - take screens on steps: %s\n' % str(config.takeScreensOnSteps))
        t = 0
        for data in reportTestSuiteData:
            if (data['testStatus'] == 0) or (data['testStatus'] == 'PASS'):
                data['testStatus'] = 'PASS'
            else:
                data['testStatus'] = 'FAIL'
            file.writelines('Thread #%d\n' % t +
                            '    last timeStart: %(timeStart)s\n' % data +
                            '    last timeStop: %(timeStop)s\n' % data +
                            '    last duration: %(duration)s\n' % data +
                            '    last testStatus: %(testStatus)s\n' % data +
                            '    Summary exception\'s statistic for thread #%d:\n' % t +
                            '        all: %(all)d\n' % reportExceptions[t] +
                            '        TimeoutException: %(TimeoutException)d\n' % reportExceptions[t] +
                            '        NoSuchElementException: %(NoSuchElementException)d\n' % reportExceptions[t])
            t += 1
        file.close()
    except Exception:
        LOGGER.error('Can not create summary file %s' % fullPath)
        LOGGER.exception('Python exception: ')
        return 1
    return 0


def GetScreen(nameOfScreen='', instance=0):
    """
    Function gets screenshot from browser and put it into png-file to the <date_time>_thread## dir format.
    """
    try:
        page = browsers[instance]
        screenDir = resultPath + "/" + config.testSuiteScreensDir
        if not (os.path.exists(screenDir)):
            os.mkdir(screenDir)
        screenDir = screenDir + '/' + threads[instance]['sTime'].strftime('%d_%m_%Y_%H_%M_%S_') + 'Thread_' + str(
            instance)
        if not (os.path.exists(screenDir)):
            os.mkdir(screenDir)
        screenFile = screenDir + '/' + datetime.now().strftime('%d_%m_%Y_%H_%M_%S_') + nameOfScreen
        if screenFile[-4:] != '.png':
            screenFile = screenFile + '.png'
        page.get_screenshot_as_file(screenFile)
        LOGGER.info('Thread #%s, Screenshot created: %s' % (str(instance), screenFile))
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, Can not create screenshot-file!' % str(instance))
        LOGGER.exception('Thread #%s, Python exception: ' % str(instance))
        return 1


def OpenBrowser(opTimeout=10, browserString='*firefox', ffProfile=None, instance=0):
    """
    Commands for opening WebDriver browser.
    """
    try:
        startTime = datetime.now()
        LOGGER.info('Thread #%s, command: OpenBrowser, start time: %s' % (str(instance), FormatTimeString(startTime)))
        # Get new browser instance and put it into browsers array. One browser for one thread.
        if browserString == '*chrome':
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--start-maximized')
            chromeOptions.add_argument('--log-path=' + workDir + '/browser_drivers/chromedriver.log')
            os.chdir(workDir + '/browser_drivers')
            browsers.append(webdriver.Chrome(executable_path=workDir + '/browser_drivers/chromedriver.exe',
                                             chrome_options=chromeOptions))
            os.chdir(workDir)
        elif browserString == '*ie':
            browsers.append(webdriver.Ie(executable_path=workDir + '/browser_drivers/IEDriverServer.exe',
                                         log_file=workDir + '/browser_drivers/iedriver.log'))
        else:
            ffp = webdriver.FirefoxProfile(ffProfile)
            browsers.append(webdriver.Firefox(firefox_profile=ffp, timeout=opTimeout))
            browsers[instance].maximize_window()
        finishTime = datetime.now()
        LOGGER.info('Thread #%s, command: OpenBrowser, finish time: %s' % (str(instance), FormatTimeString(finishTime)))
        LOGGER.info('Thread #%s, command: OpenBrowser, duration: %s' % (str(instance), str(finishTime - startTime)))
        LOGGER.info('Thread #%s, command: OpenBrowser, status: oK' % str(instance))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%s_command_OpenBrowser_status_oK' % str(instance), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, command: OpenBrowser, status: error' % str(instance))
        LOGGER.exception('Python exception: ')
        return 1


def OpenProjectAndLogin(projectURL, login, password, opTimeout=10, browserString='*firefox', ffProfile=None, instance=0):
    """
    Commands for opening project's URL and try to login.
    """
    try:
        page = browsers[instance]
        LOGGER.info('Thread #%s, command: OpenProjectAndLogin - go to project\'s URL: %s' % (str(instance), projectURL))
        startTime = datetime.now()
        LOGGER.info('Thread #%s, command: OpenProjectAndLogin, start time: %s' % (str(instance), FormatTimeString(startTime)))
        page.get(projectURL)
        try:
            # Wait main page:
            WebDriverWait(page, opTimeout).until(lambda el: el.find_element_by_xpath("//input[@type='text']"), 'Timeout while open auth page.')
            # Type domain login/pass into fields if they are avaliable. Befor it, check that fields are enabled!
            if page.find_element_by_xpath("//input[@id='login']").get_attribute('disabled') != 'true':
                page.find_element_by_xpath("//input[@id='login']").send_keys(login)
            if page.find_element_by_xpath("//input[@id='password']").get_attribute('disabled') != 'true':
                page.find_element_by_xpath("//input[@id='password']").send_keys(password)
            page.find_element_by_xpath("//*[@type='submit']").click()
        except:
            LOGGER.info('Thread #%s, command: OpenProjectAndLogin, probably you are log in already.' % str(instance))
        finishTime = datetime.now()
        LOGGER.info('Thread #%s, command: OpenProjectAndLogin, finish time: %s' % (str(instance), FormatTimeString(finishTime)))
        LOGGER.info('Thread #%s, command: OpenProjectAndLogin, duration: %s' % (str(instance), str(finishTime - startTime)))
        LOGGER.info('Thread #%s, command: OpenProjectAndLogin, status: oK' % str(instance))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%s_command_OpenProjectAndLogin_status_oK' % str(instance), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, command: OpenProjectAndLogin, status: error' % str(instance))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_OpenProjectAndLogin_status_error' % str(instance), instance)
        return 1


def CloseBrowser(instance=0):
    """
    Try to close WebDriver browser.
    """
    if (len(browsers) > 0) and (browsers[instance] != None):
        try:
            page = browsers[instance]
            startTime = datetime.now()
            LOGGER.info('Thread #%s, command: CloseBrowser, start time: %s' % (str(instance), FormatTimeString(startTime)))
            LOGGER.info('Thread #%s, command: CloseBrowser' % str(instance))
            if config.takeScreensOnSteps:
                GetScreen('Thread_%s_command_CloseBrowser_status_oK' % str(instance), instance)
            page.close()
            browsers[instance] = None
            LOGGER.info('Thread #%s, command: CloseBrowser, status: oK' % str(instance))
        except exceptions.TimeoutException:
            reportExceptions[instance]['all'] += 1
            reportExceptions[instance]['TimeoutException'] += 1
            if config.takeScreensOnError:
                GetScreen('Thread_%s_command_CloseBrowser_status_error' % str(instance), instance)
            return 1
        except exceptions.NoSuchElementException:
            reportExceptions[instance]['all'] += 1
            reportExceptions[instance]['NoSuchElementException'] += 1
            if config.takeScreensOnError:
                GetScreen('Thread_%s_command_CloseBrowser_status_error' % str(instance), instance)
            return 1
        except Exception:
            reportExceptions[instance]['all'] += 1
            LOGGER.error('Thread #%s, command: CloseBrowser, status: error' % str(instance))
            LOGGER.exception('Python exception: ')
            if config.takeScreensOnError:
                GetScreen('Thread_%s_command_CloseBrowser_status_error' % str(instance), instance)
            return 1
    return 0


def VerifyMainPageContainsSomeElements(opTimeout=10, instance=0):
    """
    Verify that some elements presents on page.
    """
    try:
        page = browsers[instance]
        startTime = datetime.now()
        LOGGER.info('Thread #%s, command: VerifyMainPageContainsSomeElements, start time: %s' % (str(instance), FormatTimeString(startTime)))
        # If we can't find elements it will be exception and we'll see it in log-file:
        page.find_element_by_xpath("//input[@type='text']")
        page.find_element_by_xpath("//span[contains(text(), 'Поиск в Google')]")
        page.find_element_by_xpath("//span[contains(text(), 'Мне повезёт!')]")
        if config.takeScreensOnSteps:
            GetScreen('Thread_%s_command_VerifyMainPageContainsSomeElements_status_oK' % str(instance), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_VerifyMainPageContainsSomeElements_status_error' % str(instance), instance)
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_VerifyMainPageContainsSomeElements_status_error' % str(instance), instance)
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, command: VerifyMainPageContainsSomeElements, status: error' % str(instance))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_VerifyMainPageContainsSomeElements_status_error' % str(instance), instance)
        return 1


def CheckSearchPage(opTimeout=10, instance=0):
    """
    Going to menu path: Administrating - Setting up synchronization.
    """
    try:
        page = browsers[instance]
        startTime = datetime.now()
        LOGGER.info('Thread #%s, command: CheckSearchPage, start time: %s' % (str(instance), FormatTimeString(startTime)))
        page.find_element_by_xpath("//input[@type='text']").send_keys('Test search')
        page.find_element_by_xpath("(//button[@aria-label='Поиск в Google'])[1]").click()
        WebDriverWait(page, opTimeout).until(
            lambda el: el.find_element_by_xpath("(//div[@id='res']/..//a)[1]").is_displayed(),
            'Timeout while we are wait result page.')
        finishTime = datetime.now()
        LOGGER.info('Thread #%s, command: CheckSearchPage, finish time: %s' % (str(instance), FormatTimeString(finishTime)))
        LOGGER.info('Thread #%s, command: CheckSearchPage, duration: %s' % (str(instance), str(finishTime - startTime)))
        LOGGER.info('Thread #%s, command: CheckSearchPage, status: oK' % str(instance))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%s_command_CheckSearchPage_status_oK' % str(instance), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_CheckSearchPage_status_error' % str(instance), instance)
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_CheckSearchPage_status_error' % str(instance), instance)
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, command: CheckSearchPage, status: error' % str(instance))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_CheckSearchPage_status_error' % str(instance), instance)
        return 1


# This file used as library of steps only
if __name__ == '__main__':
    pass
