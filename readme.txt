Параметры для консольного запуска представлены ключами:
Ключ	Слово	        Описание
-h      --help          Показать подсказку по опциям.
-c      --cases         Изменить набор тест-кейсов в тест-сьюте. Строка чисел через запятую, без пробела.
-f      --flagToRepeat  Флаг для зацикливания последовательности тест-кейсов в тест-сьюте. Укажите 'True' для зацикливания.
-b      --browser	    Строка браузера (*firefox, *chrome, *ie), показывающая, какой браузер запустить.
-t      --threads	    Число потоков для параллельного запуска.
-r	    --rumpUp	    Период (сек.), в течении которого все потоки должны быть запущены.
-l	    --login	        Логин пользователя.
-p	    --password	    Пароль пользователя.
-T      --timeout       Таймаут операций в сек.
-u      --URL           URL проекта .
-e      --takeErrScr    Укажите '-e False' если вы хотите делать скриншоты только при ошибке.
-a      --takeAllScr    Укажите '-a False' если вы хотите делать скриншоты при любых операциях.
-s      --sortThreads   Укажите '-s <log-file>' для сортировки некоторого лог-файла по тредам.

Если ключи не указаны, используются настройки по  умолчанию из файла config.py. Ключи, указанные при запуске в консоли
имеют больший приоритет, чем настройки по умолчанию из config.py!

Находясь в корне проекта для запуска тестов можно использовать следующие команды.

Для параллельного запуска всех тестовых наборов в нескольких потоках
с указанными в config.py настройками по умолчанию или переданными через консоль параметрами:

python tester.py [options]

Примеры:
    python tester.py --cases=[1,2,1,2,1,2] # Запуск измененной последовательности тест-кейсов. Вводятся без пробела.
    python tester.py -f True # Зациклить прохождение набора тест-кейсов в тест-сьюте.
    python tester.py -b *ie # Запуск тестов в ie, остальные параметры по умолчанию.
    python tester.py -b *firefox --threads=2 --rumpUp=5 # Запуск тестов в ff, число потоков 2, время старта 5 сек, остальные параметры по умолчанию.
    python tester.py --browser='*chrome' -t 1 -r 1 --login=mylogin -p pass # Запуск тестов в chrome, с указанием числа потоков, времени старта, логина и пароля.
    python tester.py -b *chrome -T 5 # Запуск тестов в хроме с таймаутом операций в 5 сек, остальные операции по умолчанию.
    python tester.py -b *ie -e True -a False # Запуск тестов в ie, делать скриншоты только при ошибках, остальные операции по умолчанию.
    python tester.py -u https://google.ru -a False # Запустить тесты с указанием основного URL.
    python tester.py --sortThreads reports/Log.txt # Отсортировать и разбить указанный лог-файл по тредам. Результат идет в reports/logs/
    python tester.py --sortThreads default # Отсортировать стандартный лог-файл по разным тредам. Результат идет в reports/logs/

Для запуска только одного тестового набора в один поток с указанными в config.py настройками по умолчанию:

python gui_test_suites.py

Для запуска только одного тест-кейса в один поток с указанными в config.py настройками по умолчанию:

python tests/test_case_1_Init_test.py


Для отладки конкретного тест-кейса нужно ставить рабочей директорией корень проекта (каталог GUItests).
Для разработки теста можно скопировать любой имеющийся пример из каталоге tests и сделать свой тест по аналогии.
Можно добавлять свои пользовательские переменные в config.py.


Структура файлов и каталогов по умолчанию:

GUItests - корень проекта.
    /tests - пакет, в которых хранятся отдельные тест-кейсы.
        test_case_1_Init_test.py - пример одного тест-кейса, составленный из отдельных шагов.
    /ff_profile - каталог с необходимым профилем для mozilla.
    /reports - каталог с логами и всеми результатами, как для случая запуска всех тест-сьютов через tester.py,
           так и в случае запуска отдельного тест-сьюта или тест-кейса.
        /screens - каталог со скриншотами.
            /<date_time>_thread## - каталоги со скриншотами для различных тредов, с указанием в начале даты и времени.
                <date_time>_thread##_Step_<step_name>_command_<command_name>_status_<status>.png - файл со скриншотом,
                содержащий дату и время его создания, номер треда, название шага и действия, статус действия.
    config.py - сюда выносятся все глобальные настройки для тестов, каждый параметр прокомментирован.
    steps_Lib.py - библиотека отдельных логических шагов для тестов и вспомогательных функций.
                   Каждый шаг может состоять из нескольких действий. Тест-кейсы сюда не вносятся!
    gui_Test_suite.py - здесь описывается структура тест-сьюта, который управляет запуском
                        набора тест-кейсов. Каждый тест-кейс описан в отдельном файле.
    tester.py - скрипт для многопоточного запуска указанных тест-сьютов с настройками из config.py.
                По аналогии можно добавить запуск других классов тест-сьютов.


Начинать имена тестовых шагов лучше по смыслу: GoTo, Edit, Verify, Click и т.п.
Пример оформления функции - одного шага для теста и обязательные команды в теле функции:

def NameOfFunctionStep(opTimeout=10, instance=0):
    """
    Description.
    """
    try:
        # Initialization steps for function:
        page = browsers[instance]
        startTime = datetime.now()
        LOGGER.info('Thread #%s, command: NameOfFunctionStep, start time: %s' %
                    (str(instance), FormatTimeString(startTime)))

        # Insert your steps and actions here.

        # Finalization steps for function:
        finishTime = datetime.now()
        LOGGER.info('Thread #%s, command: NameOfFunctionStep, finish time: %s' %
                    (str(instance), FormatTimeString(finishTime)))
        LOGGER.info('Thread #%s, command: NameOfFunctionStep, duration: %s' %
                    (str(instance), str(finishTime - startTime)))
        LOGGER.info('Thread #%s, command: NameOfFunctionStep, status: oK' % str(instance))
        if config.takeScreensOnSteps:
            GetScreen('Thread_%s_command_NameOfFunctionStep_status_oK' % str(instance), instance)
        return 0
    except exceptions.TimeoutException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['TimeoutException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_NameOfFunctionStep_status_error' % str(instance), instance)
        return 1
    except exceptions.NoSuchElementException:
        reportExceptions[instance]['all'] += 1
        reportExceptions[instance]['NoSuchElementException'] += 1
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_NameOfFunctionStep_status_error' % str(instance), instance)
        return 1
    except Exception:
        reportExceptions[instance]['all'] += 1
        LOGGER.error('Thread #%s, command: NameOfFunctionStep, status: error' % str(instance))
        LOGGER.exception('Python exception: ')
        if config.takeScreensOnError:
            GetScreen('Thread_%s_command_NameOfFunctionStep_status_error' % str(instance), instance)
        return 1
