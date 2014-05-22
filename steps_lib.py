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
from datetime import timedelta
import time
import threading
import random
import urllib
import urllib.request
import urllib.parse
import argparse
import subprocess
import re


# Working Directory.
workDir = os.path.abspath(os.curdir)

# Full Path to report directory
resultPath = os.path.join(workDir, config.testSuiteReportDir)

# List of test-suite threads with start time. This is dictionaries: {'thread': <thread>, 'sTime': <start_time>}
threads = []

# List of browsers - one browser in every thread.
browsers = []

# List of dictionaries for test-suite results only. Dict's format:
# {'thread': <thread>,
#  'timeStart': <start>,
#  'timeStop': <stop>,
#  'duration': <stop-start>,
#  'testStatus': <status>}
reportTestSuiteData = []
reportTestCaseData = []
reportByThreads = []

# List of dictionaries for Exception's statistic by threads. Dict's format:
# {'total': <num>, 'TimeoutException': <num>, 'NoSuchElementException': <num>}
reportExceptions = []


# Settings for LOGGER:
try:
    if not (os.path.exists(resultPath)):
        os.mkdir(resultPath)
    if not os.path.exists(os.path.join(resultPath, 'logs')):
        os.mkdir(os.path.join(resultPath, 'logs'))
    LOGGER = logging.getLogger('Test Logger')
    LOGGER.setLevel(config.loggerInfoLevel)
    handler = logging.FileHandler(os.path.join(resultPath,  config.testSuitesLogFile))
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
except Exception:
    print('Can\'t start LOGGER!')
    sys.exit(1)


def GetPIDListOfProgramm(name):
    """
    Function returns list of numbers of process pids for Selenium browser's drivers.
    Warning! This function works very slow!
    """
    pids = []
    try:
        tasklist = subprocess.Popen(['tasklist'], stdout=subprocess.PIPE)
        (stdout, stderr) = tasklist.communicate()
        for process in stdout.decode('cp866').split('\n'):
            if name in process:
                nums = re.findall("(?! )\d+(?!= )", process)
                if nums:
                    pids.append(nums[0])
    except Exception:
        traceback.print_exc()
    finally:
        pids = sorted(sorted(pids), key=lambda x: len(x))
        for i in range(len(pids)):
            pids[i] = int(pids[i])
        return pids


def KillProcess(pid):
    """
    This function stops process with given pid.
    """
    statusCode = 0
    try:
        if pid >= 0:
            cmd = "taskkill /F /T /PID {0} > NUL 2>&1".format(pid)
            os.system(cmd)
            LOGGER.debug('Process killed: ' + str(pid))
        else:
            raise Exception('Error! Process %d does not stop!' % pid)
    except Exception:
        LOGGER.exception('Python exception: ')
        statusCode = 1
    finally:
        return statusCode


def Cleaner():
    """
    This function use for finalization operations of test.
    """
    LOGGER.debug('Cleaner working...')
    chromePIDs = GetPIDListOfProgramm('chromedriver.exe')
    for pid in chromePIDs:
        KillProcess(pid)
    iePIDs = GetPIDListOfProgramm('IEDriverServer.exe')
    for pid in iePIDs:
        KillProcess(pid)
    LoggerParserByThreads(os.path.join(resultPath, config.testSuitesLogFile), config.testSuiteThreads)
    LOGGER.info('Cleaner finished work. All test-process stoped.')


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
        LOGGER.exception('Python exception: ')
        return []
    return numList


def LoggerParserByThreads(summaryLogFile, threadsNum=1):
    """
    Get summary log file and parse it by separate thread.
    """
    if os.path.exists(summaryLogFile):
        for t in range(threadsNum):
            try:
                logFile = os.path.join(resultPath, 'logs', datetime.now().strftime('%d_%m_%Y_%H_%M_%S_') + 'Thread_' + str(t))
                if not (os.path.exists(logFile)):
                    os.mkdir(logFile)
                logFile = os.path.join(logFile, 'Thread_' + str(t))
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
                LOGGER.exception('Python exception: ')
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
                'Thread;timeStart;timeStop;duration;testStatus;total_exceptions;TimeoutException;NoSuchElementException\n')
        for data in reportByThreads:
            if (data['testStatus'] == 0) or (data['testStatus'] == 'PASS'):
                data['testStatus'] = 'PASS'
            else:
                data['testStatus'] = 'FAIL'
        for data in reportByThreads:
            if data['thread'] == threadNum:
                file.writelines('%(thread)d;%(timeStart)s;%(timeStop)s;%(duration)s;%(testStatus)s;' % data +
                                '%(total)d;%(TimeoutException)d;%(NoSuchElementException)d\n' %
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
    if args.flagToRepeat:
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
    return timeAndDate.strftime('%Y-%m-%d %H:%M:%S')


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
        file.write('    - repeat case sequence: %s\n' % str(config.repeatCaseSequence))
        file.write('    - time to stop stress test (sec.): %s\n' % str(config.timeToStopTests))
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
                            '        total errors: %(total)d\n' % reportExceptions[t] +
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
        if instance > 0 and instance < len(browsers):
            page = browsers[instance]
            screenDir = os.path.join(resultPath, config.testSuiteScreensDir)
            if not (os.path.exists(screenDir)):
                os.mkdir(screenDir)
            screenDir = os.path.join(screenDir, threads[instance]['sTime'].strftime('%d_%m_%Y_%H_%M_%S_') + 'Thread_%d' % instance)
            if not (os.path.exists(screenDir)):
                os.mkdir(screenDir)
            screenFile = os.path.join(screenDir, datetime.now().strftime('%d_%m_%Y_%H_%M_%S_') + nameOfScreen)
            if screenFile[-4:] != '.png':
                screenFile = screenFile + '.png'
            page.get_screenshot_as_file(screenFile)
            LOGGER.info('Thread #%d, Screenshot created: %s' % (instance, screenFile))
        else:
            raise Exception('GetScreen error: instance = %d, len(browsers) = %s, but browser was closed earlier.' % (instance, str(len(browsers))))
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['total'] += 1
        LOGGER.error('Thread #%d, Can not create screenshot-file!' % instance)
        LOGGER.exception('Thread #%d, Python exception: ' % instance)
        return 1


def OpenBrowser(opTimeout=10, browserString='*firefox', ffProfile=None, instance=0):
    """
    Commands for opening WebDriver browser.
    """
    currentFuncName = sys._getframe().f_code.co_name  # get current function name for message templates
    try:
        startTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, start time: %s' % (instance, currentFuncName, FormatTimeString(startTime)))
        # Get new browser instance and put it into browsers array. One browser for one thread.
        if browserString == '*chrome':
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--start-maximized')
            chromeOptions.add_argument('--log-path=' + os.path.join(workDir, 'browser_drivers', 'chromedriver.log'))
            os.chdir(os.path.join(workDir, 'browser_drivers'))
            browsers.append(webdriver.Chrome(executable_path=os.path.join(workDir, 'browser_drivers', 'chromedriver.exe'),
                                             chrome_options=chromeOptions))
            os.chdir(workDir)
        elif browserString == '*ie':
            browsers.append(webdriver.Ie(executable_path=os.path.join(workDir, 'browser_drivers', 'IEDriverServer.exe'),
                                         log_file=os.path.join(workDir, 'browser_drivers', 'iedriver.log')))
        else:
            ffp = webdriver.FirefoxProfile(ffProfile)
            browsers.append(webdriver.Firefox(firefox_profile=ffp, timeout=opTimeout))
            browsers[instance].maximize_window()
        finishTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, finish time: %s' % (instance, currentFuncName, FormatTimeString(finishTime)))
        LOGGER.info('Thread #%d, command: %s, duration: %s' % (instance, currentFuncName, str(finishTime - startTime)))
        LOGGER.info('Thread #%d, command: %s, status: oK' % (instance, currentFuncName))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%d_command_%s_status_oK' % (instance, currentFuncName), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['total'] += 1
        LOGGER.error('Thread #%d, command: %s, status: error' % (instance, currentFuncName))
        LOGGER.exception('Python exception: ')
        return 1


def OpenProjectAndLogin(projectURL, login, password, opTimeout=10, browserString='*firefox', ffProfile=None, instance=0):
    """
    Commands for opening project's URL and try to login.
    """
    currentFuncName = sys._getframe().f_code.co_name  # get current function name for message templates
    try:
        page = browsers[instance]
        LOGGER.info('Thread #%d, command: %s - go to project\'s URL: %s' % (instance, currentFuncName, projectURL))
        startTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, start time: %s' % (instance, currentFuncName, FormatTimeString(startTime)))
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
            LOGGER.info('Thread #%d, command: %s, probably you are log in already.' % (instance, currentFuncName))
        finishTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, finish time: %s' % (instance, currentFuncName, FormatTimeString(finishTime)))
        LOGGER.info('Thread #%d, command: %s, duration: %s' % (instance, currentFuncName, str(finishTime - startTime)))
        LOGGER.info('Thread #%d, command: %s, status: oK' % (instance, currentFuncName))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%d_command_%s_status_oK' % (instance, currentFuncName), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        return 1
    except Exception:
        reportExceptions[instance]['total'] += 1
        LOGGER.error('Thread #%d, command: %s, status: error' % (instance, currentFuncName))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1


def CloseBrowser(instance=0):
    """
    Try to close WebDriver browser.
    """
    currentFuncName = sys._getframe().f_code.co_name  # get current function name for message templates
    if (len(browsers) > 0) and (browsers[instance] != None):
        try:
            page = browsers[instance]
            startTime = datetime.now()
            LOGGER.info('Thread #%d, command: %s, start time: %s' % (instance, currentFuncName, FormatTimeString(startTime)))
            LOGGER.info('Thread #%d, command: %s' % (instance, currentFuncName))
            if config.takeScreensOnSteps:
                GetScreen('Thread_%d_command_%s_status_oK' % (instance, currentFuncName), instance)
            page.close()
            browsers[instance] = None
            LOGGER.info('Thread #%d, command: %s, status: oK' % (instance, currentFuncName))
        except exceptions.TimeoutException:
            reportExceptions[instance]['total'] += 1
            reportExceptions[instance]['TimeoutException'] += 1
            if config.takeScreensOnError:
                GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
            return 1
        except exceptions.NoSuchElementException:
            reportExceptions[instance]['total'] += 1
            reportExceptions[instance]['NoSuchElementException'] += 1
            if config.takeScreensOnError:
                GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
            return 1
        except Exception:
            reportExceptions[instance]['total'] += 1
            LOGGER.error('Thread #%d, command: %s, status: error' % (instance, currentFuncName))
            LOGGER.exception('Python exception: ')
            if config.takeScreensOnError:
                GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
            return 1
    return 0


def VerifyMainPageContainsSomeElements(opTimeout=10, instance=0):
    """
    Verify that some elements presents on page.
    """
    currentFuncName = sys._getframe().f_code.co_name  # get current function name for message templates
    try:
        page = browsers[instance]
        startTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, start time: %s' % (instance, currentFuncName, FormatTimeString(startTime)))
        # If we can't find elements it will be exception and we'll see it in log-file:
        page.find_element_by_xpath("//input[@type='text']")
        page.find_element_by_xpath("//span[contains(text(), 'Поиск в Google')]")
        page.find_element_by_xpath("//span[contains(text(), 'Мне повезёт!')]")
        if config.takeScreensOnSteps:
            GetScreen('Thread_%d_command_%s_status_oK' % (instance, currentFuncName), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1
    except Exception:
        reportExceptions[instance]['total'] += 1
        LOGGER.error('Thread #%d, command: %s, status: error' % (instance, currentFuncName))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1


def CheckSearchPage(opTimeout=10, instance=0):
    """
    Going to menu path: Administrating - Setting up synchronization.
    """
    currentFuncName = sys._getframe().f_code.co_name  # get current function name for message templates
    try:
        page = browsers[instance]
        startTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, start time: %s' % (instance, currentFuncName, FormatTimeString(startTime)))
        page.find_element_by_xpath("//input[@type='text']").send_keys('Test search')
        page.find_element_by_xpath("(//button[@aria-label='Поиск в Google'])[1]").click()
        WebDriverWait(page, opTimeout).until(
            lambda el: el.find_element_by_xpath("(//div[@id='res']/..//a)[1]").is_displayed(),
            'Timeout while we are wait result page.')
        finishTime = datetime.now()
        LOGGER.info('Thread #%d, command: %s, finish time: %s' % (instance, currentFuncName, FormatTimeString(finishTime)))
        LOGGER.info('Thread #%d, command: %s, duration: %s' % (instance, currentFuncName, str(finishTime - startTime)))
        LOGGER.info('Thread #%d, command: %s, status: oK' % (instance, currentFuncName))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%d_command_%s_status_oK' % (instance, currentFuncName), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['total'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1
    except Exception:
        reportExceptions[instance]['total'] += 1
        LOGGER.error('Thread #%d, command: %s, status: error' % (instance, currentFuncName))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%d_command_%s_status_error' % (instance, currentFuncName), instance)
        return 1


# This file used as library of steps only! Not for run!
if __name__ == '__main__':
    pass
