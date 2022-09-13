import traceback
from datetime import datetime, timedelta
# import urllib.request
import cloudinary.uploader
from pytz import timezone
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import requests
from bs4 import BeautifulSoup

import bot_token

groups = {'ІТКН-18-7': '6949698', 'ІТКН-18-8': '6949806', 'ІТКН-18-9': '6949662',
          'ІТШІ-18-1': '6949664', 'ІТШІ-18-2': '7193698'}
url_users = 'https://res.cloudinary.com/dnmx4vd6f/raw/upload/users.txt'
url_tables = 'https://res.cloudinary.com/dnmx4vd6f/raw/upload/v1635238176/timetables.txt'
Dates = {'Понеділок', 'Вівторок', 'Середа', 'Четвер', "П'ятниця", 'Субота', 'Неділя'}
url_nure = 'https://dl.nure.ua/my/'
none = '&nbsp'
admin = '573958202'
nums = [0, 1, 2, 3, 4, 5, 6]
table_list, user_list = {}, {}
minut_do = 5
if_get_tables = False

Tag = {
    'nametimetable': '<nametimetable>',
    'timetable': '<timetable>',
    'day': '<day>',
    'date': '<date>',
    'time': '<time>',
    'number': '<number>',
    'lessons': '<lessons>',
    'lesson': '<lesson>',
    'namelesson': '<namelesson>',
    'id': '<id>',
    'nic': '<nic>',
    'user': '<user>',
    'minut_do': '<minut_do>'
}
attendance = {
    'ІТвІSW': 'https://dl.nure.ua/mod/attendance/view.php?id=187371',
    'ПScala': 'https://dl.nure.ua/mod/attendance/view.php?id=187359',
    'Пр.NET': 'Отмечаться нужно плюсиком в чате мита в конце занятия',
    'ШНМнз': 'https://dl.nure.ua/course/view.php?id=8892',
    'UI/UX': 'https://dl.nure.ua/mod/attendance/view.php?id=260025',
    'СРШІ': 'https://dl.nure.ua/mod/attendance/view.php?id=249499',
    'Ек&Б': 'https://dl.nure.ua/mod/attendance/view.php?id=256015',
    'А Scala та Spark': 'https://dl.nure.ua/mod/attendance/view.php?id=249331',
}

links = {
    'meet': {
        'lecture': {
            'ІМТА': 'https://meet.google.com/sez-tams-you',
            'ІТвІSW': 'https://meet.google.com/dwt-jyuo-rix',
            'МПтОпт': 'https://meet.google.com/frn-gynj-wkb',
            'ПScala': 'https://meet.google.com/ena-dczm-eym',
            'Пр.NET': 'https://meet.google.com/hkw-efky-ivk',
            'ШНМнз': 'https://meet.google.com/mnw-otzr-yed',
            'UI/UX': 'https://meet.google.com/sus-hjrh-qcj',
            'СРШІ': 'https://meet.google.com/eqd-cwuz-ogh',
            'Ек&Б': 'https://meet.google.com/vkt-kwxt-oxd',
            'А Scala та Spark': 'https://meet.google.com/dbf-cypf-fo',
        },
        'practic': {
            'ІМТА': 'https://meet.google.com/sez-tams-you',
            'ІТвІSW': 'Бібічков І.Є. -> https://meet.google.com/ggr-qcnw-pnc'
                      '\nПоліїт М.Р. -> https://meet.google.com/tsw-tpyu-eih',
            'МПтОпт': 'https://meet.google.com/frn-gynj-wkb',
            'ПScala': 'https://meet.google.com/ena-dczm-eym',
            'Пр.NET': 'Губін В.О. -> https://meet.google.com/ctn-otxe-eys',
            'ШНМнз': 'https://meet.google.com/mnw-otzr-yed',
            'UI/UX': 'https://meet.google.com/agx-vdhs-mmf',
            'СРШІ': 'https://meet.google.com/eqd-cwuz-ogh',
            'А Scala та Spark': 'https://meet.google.com/dbf-cypf-fo',
        },
    }
}


def unxml_list(text, tag):
    # развертывает множество фраз одного тега в список
    detag = tag[0] + '/' + tag[1:]
    tag_list = []
    while text.find(tag) != -1 and text.find(detag) != -1:
        tag_list.append(text[text.find(tag) + len(tag):text.find(detag)])
        text = text[text.find(detag) + len(detag):]
    return tag_list


def unxml(text, tag):
    # Развертывает фразу из тега
    detag = tag[0] + '/' + tag[1:]
    if text.find(tag) != -1 and text.find(detag) != -1:
        return text[text.find(tag) + len(tag):text.find(detag)]


def toxml(text, tag):
    # Оборачивает фразу в тег
    return str(tag) + str(text) + str(tag)[0] + '/' + str(tag)[1:]


def replacexml(text, replacement, tag):
    # хмл - меняет содержимое в text на replacement в теге tag
    detag = tag[0] + '/' + tag[1:]
    data = text[text.find(tag):text.find(detag) + len(detag)]
    return text.replace(data, toxml(replacement, tag))


def write_table():
    if if_get_tables:
        f = open('timetables.txt', 'w', encoding='cp1251')
        all_text = ''
        for group in groups:
            data = toxml(group, Tag['nametimetable']) + '\n'

            for day in lessons[group]:
                for lesson in day:
                    textless = toxml(lesson[0], Tag['date']) + '\n'
                    if len(lesson) > 1:
                        for per in lesson[1:]:
                            less = toxml(per[0], Tag['number']) + toxml(per[1], Tag['time']) + toxml(per[2],
                                                                                                     Tag['namelesson'])
                            textless += toxml(less, Tag['lesson']) + '\n'
                        data += toxml(textless, Tag['day']) + '\n'
            all_text += toxml(data, Tag['timetable'])
        f.write('\n' + all_text)
        f.close()


def read_tables():
    # считать расписание из файла в массив
    global table_list
    f = open('timetables.txt', 'r', encoding='cp1251')
    file = f.read()
    timetables = unxml_list(file, Tag['timetable'])
    if timetables:
        for table in timetables:
            name_table = unxml(table, Tag['nametimetable'])
            table_list[name_table] = []
            days = unxml_list(table, Tag['day'])
            for day in days:
                table_list[name_table].append([unxml(day, Tag['date'])])
                lessons = unxml_list(day, Tag['lesson'])
                for lesson in lessons:
                    number = unxml(lesson, Tag['number'])
                    time = unxml(lesson, Tag['time'])
                    namelesson = unxml(lesson, Tag['namelesson'])
                    table_list[name_table][-1].append([number, time, namelesson])
    f.close()


def get_predmets():
    # Парсит сайт расписания для получения списка предметов и преподов
    if if_get_tables:
        now = datetime.now()
        data = str(now)[:10].split('-')
        now_day, now_month = data[2], data[1]
        for group in groups:
            url = 'https://cist.nure.ua/ias/app/tt/f?p=778:201:3794466796183216:::201:P201_FIRST_DATE,P201_LAST_DATE,' \
                  'P201_GROUP,P201_POTOK:' + now_day + '.' + now_month + '.2022,30.07.2022,' + groups[group] + ',0:'
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'lxml')

            table_predmet = soup.find('table', class_='footer')
            tdpr = table_predmet.find_all('tr')
            for t in tdpr:
                predmets[group].append({})
                predmet = t.find_all('td')
                a = predmet[1].find_all('a')
                if len(a) == 2:
                    predmets[group][-1]['lector'] = predmet[1].find_all('a', class_='linktt')[0].text  # лектор
                    predmets[group][-1]['practic'] = predmet[1].find_all('a', class_='linktt')[1].text  # практик
                else:
                    if len(a) == 4:
                        predmets[group][-1]['lector'] = predmet[1].find_all('a', class_='linktt')[1].text  # лектор
                        predmets[group][-1]['practic'] = predmet[1].find_all('a', class_='linktt')[3].text  # практик
                    else:
                        predmets[group][-1]['lector'] = None  # лектор
                        predmets[group][-1]['practic'] = None  # практик
                predmets[group][-1]['short_name'] = predmet[0].find('a').text.replace('*', '')  # название короткое
                predmets[group][-1]['long_name'] = predmet[1].text.split(' : ')[0]  # длинное короткое
                predmets[group][-1]['lectures'] = predmet[1].text[
                                                  predmet[1].text.find('Лк ('):predmet[1].text.find('Лк (') + 7]  #
                predmets[group][-1]['practics'] = predmet[1].text[
                                                  predmet[1].text.find('Пз ('):predmet[1].text.find('Пз (') + 7]  #


def get_timetable():
    # Парсит сайт расписания, получает массив лессонс с ним
    global dates, days, lessons, predmets, if_get_tables
    dates, days, lessons, predmets = {}, {}, {}, {}
    now = datetime.now()
    data = str(now)[:10].split('-')
    now_day, now_month = data[2], data[1]
    try:
        for group in groups:
            dates[group], days[group], lessons[group], predmets[group] = [], [], [], []
            url = 'https://cist.nure.ua/ias/app/tt/f?p=778:201:3794466796183216:::201:P201_FIRST_DATE,P201_LAST_DATE,' \
                  'P201_GROUP,P201_POTOK:' + now_day + '.' + now_month + '.2022,30.07.2022,' + groups[
                      group] + ',0:'  # 31.01.2022
            print('!! Получение расписаний ' + group)
            import time as t
            t.sleep(3)
            # https://cist.nure.ua/ias/app/tt/f?p=778:201:3794466796183216:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.02.2022,30.07.2022,6949664,0:
            # https://cist.nure.ua/ias/app/tt/f?p=778:201:3794466796183216:::201:P201_FIRST_DATE,P201_LAST_DATE,P201_GROUP,P201_POTOK:01.02.2022,30.07.2022,6949662,0:
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'lxml')
            table = soup.find('table', class_='MainTT')
            tr = table.find_all('tr')

            print('!! Дананые расписаний получены')
            per = False
            for t in tr:  # вынуть дни недели и строки уроков этих дней
                if set(t.text.split()) & Dates:
                    per = False
                if not per:
                    if set(t.text.split()) & Dates:
                        dates[group].append([])
                        days[group].append([])
                        td = t.find_all('td')
                        for dat in td[1:]:
                            dates[group][-1].append(dat)
                        per = True
                        continue
                if per:
                    days[group][-1].append(t)

            for date, day, num in zip(dates[group], days[group], nums):
                lessons[group].append([])  # день недели
                for dat in date:
                    lessons[group][-1].append([])
                    lessons[group][-1][-1].append(dat.text)  # записали числа в лессонс
                if day:
                    for predm in day:
                        td = predm.find_all('td')
                        n = 0
                        n_para = td[0].text
                        time = td[1].text
                        for t in td[2:]:
                            if t.text != none:
                                try:
                                    col = t['colspan']
                                    for r in range(n, n + int(col)):
                                        lessons[group][num][r].append(
                                            [n_para, time, t.text.replace('\n', '').replace('*', '')])
                                        # print(t.text.replace('\n', '').replace('*', ''))
                                    n += int(col) - 1
                                except:
                                    lessons[group][num][n].append(
                                        [n_para, time, t.text.replace('\n', '').replace('*', '')])
                                    # print(t.text.replace('\n', '').replace('*', ''))
                            n += 1
        if_get_tables = True
        write_table()
        read_tables()
        update_tables_un()
    except:
        if_get_tables = False
        print('!! ОШИБКА В ПОЛУЧЕНИИ РАСПИСАНИЙ')
        write_old_table()


def write_old_table():
    try:
        html = requests.get(url_tables)
        soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
        file = unxml(str(soup), '<body>')
        f = open('timetables.txt', 'w', encoding='cp1251')
        f.write(file)
        f.close()
        read_tables()
        print('!! Данные запасных расписаний скачаны')
    except:
        print('!! ОШИБКА В СКАЧИВАНИИ ЗАПАСНЫХ РАСПИСАНИЙ')


def get_timetables():
    # обновляет таблицу расписания, предметов-преподов, записывает расписание в файл, читает его в переменную
    get_timetable()
    get_predmets()
    print('!! Расписание обновлено')


def is_number(numbers):
    # Проверяет аргументы команды /set на наличие цифр (номера предмета)
    for num in numbers:
        if not num.isdigit():
            return False
    return True


def generate_answer(text):
    # дает ответ пользователю на любое смс (не реализована)
    return 'Что то не так...'


def update_users_un():
    try:
        cloudinary.uploader.upload("users.txt", public_id="users", resource_type="raw", invalidate=True)
        print('!! Юзеры успешно загружены в облако')
    except:
        print('!! ОШИБКА В ОБНОВЛЕНИИ ЮЗЕРОВ В ОБЛАКЕ')


def update_users_dw():
    try:
        html = requests.get(url_users)
        soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
        file = unxml(str(soup), '<body>').replace('&amp;', '&')
        f = open('users.txt', 'w', encoding='cp1251')
        f.write(file)
        f.close()
        read_user()
        print('!! Данные пользователей скачаны')
    except:
        print('!! ОШИБКА В СКАЧИВАНИИ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ')


def update_tables_un():
    try:
        cloudinary.uploader.upload("timetables.txt", public_id="timetables", resource_type="raw", invalidate=True)
        print('!! Расписания успешно загружены в облако')
    except:
        print('!! ОИБКА В ОБНОВЛЕНИИ РАСПИСАНИЙ В ОБЛАКЕ')


def update_tables_dw():
    try:
        html = requests.get(url_tables)
        soup = BeautifulSoup(html.content.decode('cp1251', 'ignore'), features="lxml")
        file = unxml(str(soup), '<body>')
        f = open('timetables.txt', 'w', encoding='cp1251')
        f.write(file)
        f.close()
        read_tables()
        print('!! Данные расписаний скачаны')
    except:
        print('!! ОШИБКА В СКАЧИВАНИИ ДАННЫХ РАСПИСАНИЙ')


def apd_user(id, minutes):
    # Юзер изменил время напоминания о предмете
    f = open('users.txt', 'r', encoding='cp1251')
    file = f.read()
    users = unxml_list(file, Tag['user'])
    for user in users:
        id_user = int(unxml(user, Tag['id']))
        if id_user == id:
            user_new = replacexml(user, minutes, Tag['minut_do'])
            users.remove(user)
            users.append(user_new)
            f.close()
            f = open('users.txt', 'w', encoding='cp1251')
            text = ''
            for len in users:
                text += toxml(len, Tag['user']) + '\n\n'
            f.write(text)
            break
    f.close()
    update_users_un()
    read_user()
    unset_user(id, False)
    set_lessons_user(id)
    print('!! Пользователь обновил время:', id, minutes)


def add_user(id, table, lessons, nic=''):
    # Командой /set юзер задал свои предметы и ф-я записала его в файлик
    f = open('users.txt', 'r', encoding='cp1251')
    file = f.read()
    users = unxml_list(file, Tag['user'])
    for user in users:
        id_user = int(unxml(user, Tag['id']))
        if id_user == id:
            users.remove(user)
            f.close()
            f = open('users.txt', 'w', encoding='cp1251')
            text = ''
            for len in users:
                text += toxml(len, Tag['user']) + '\n\n'
            f.write(text)
            break
    f.close()
    f = open('users.txt', 'a', encoding='cp1251')
    text = toxml(id, Tag['id']) + toxml(nic, Tag['nic']) + toxml(table, Tag['nametimetable'])
    lessons_text = ''
    for lesson in lessons:
        lessons_text += toxml(lesson, Tag['lesson'])
    text += lessons_text + toxml(minut_do, Tag['minut_do'])
    f.write('\n' + toxml(text, Tag['user']) + '\n\n')
    f.close()
    update_users_un()
    read_user()
    print('!! Добавлен пользователь:', id, table, lessons)


def read_user():
    # Читает из файлика всех юзеров в переменную
    f = open('users.txt', 'r', encoding='cp1251')
    file = f.read()
    users = unxml_list(file, Tag['user'])
    for user in users:
        id_user = int(unxml(user, Tag['id']))
        nametable = unxml(user, Tag['nametimetable'])
        lessons_of_user = unxml_list(user, Tag['lesson'])
        minutes = unxml(user, Tag['minut_do'])
        nic = unxml(user, Tag['nic'])
        user_list[id_user] = {'nic': nic, 'nametimetable': nametable, 'lessons': lessons_of_user, 'minut_do': minutes}
    f.close()


def alarm(context: CallbackContext) -> None:
    # Обратная функция, отправляет смс о предмете используя имя напоминания
    context.bot.send_message(context.job.context, text=context.job.name[context.job.name.find(':') + 1:],
                             parse_mode='markdown')
    text = context.job.name
    try:
        id_user = text[0:text.find(':')]
        user = user_list[int(id_user)]['nic']
        print(user, text.replace('\n', '\\n'))
    except:
        print(text.replace('\n', '\\n'))


def upd_alarm(context: CallbackContext) -> None:
    # context.bot.send_message(context.job.context, text=context.job.name, parse_mode='markdown')
    'ЗАПУСТИЛОСЬ ЕЖЕДНЕВНОЕ ОБНОВЛЕНИЕ'
    # admin_sms('Расписание успешно обновлено, бот работает.')
    upd()


def get_uts():
    dif = datetime.now().hour - datetime.utcnow().hour
    ukraine_time = timezone('Europe/Kiev')
    d_uk = datetime.now(ukraine_time)
    uts = int(str(d_uk.utcoffset())[0])
    return uts - dif


def upd(user=False):
    update_table()
    t = datetime.now()
    time = datetime(t.year, t.month, t.day, 6 - get_uts(), 0, 0, 0) + timedelta(days=1)
    if not user:
        updater.job_queue.run_once(upd_alarm, time, context=int(admin), name='update' + str(time))
        if not if_get_tables:
            time = datetime(t.year, t.month, t.day, t.hour - get_uts(), t.minute, 0, 0) + timedelta(minutes=30)

            updater.job_queue.run_once(upd_alarm, time, context=int(admin), name='update' + str(time))


def set_alarm(chat_id, t, text) -> None:
    current_jobs = updater.job_queue.get_jobs_by_name(str(chat_id) + ':' + text)
    time = datetime(t.year, t.month, t.day, t.hour - get_uts(), t.minute, 0, 0)

    if current_jobs:
        for job in current_jobs:
            date = job.trigger.run_date
            if date.year == time.year and date.month == time.month and date.day == time.day and \
                    date.hour == time.hour and date.minute == time.minute:
                return
    updater.job_queue.run_once(alarm, time, context=chat_id, name=str(chat_id) + ':' + text)


def warning(lesson, time):
    # Что будет написано в уведомлении о том что пара скоро начнется
    answer = '🟢 Напоминаю, в ' + time + ' начнется пара!\n' + lesson
    way = 'lecture' if lesson.find('Лк') else 'practic'
    for predmet in links['meet'][way]:
        if lesson.find(predmet) != -1:
            answer += '\nВот [ссылка](' + links['meet'][way][predmet] + ') на мит\n'
    return answer


def start_lesson(lesson):
    # Что будет написано в уведомлении о том что пара началась
    predmet = lesson.split(' Лк')[0].split(' Пз')[0].split(' Екз')[:1]
    url = attendance[predmet[0]] if set(predmet) & set(attendance) else url_nure
    return '🔴 Началась пара, отметься!\n' + lesson + '\n' + url


def job_if_exists(name: str, time) -> bool:
    # Проверить работу с заданным именем. Возвращает, была ли работа
    current_jobs = updater.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    return True


def remove_job_if_exists(name: str) -> bool:
    # Удалить работу с заданным именем. Возвращает, была ли работа удалена
    current_jobs = updater.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def unset(chat_id, name) -> None:
    # Удаляет одно напоминание по имени
    job_removed = remove_job_if_exists(str(chat_id) + ':' + name)
    text = str(chat_id)
    text += ' Удалила все свои напоминания' if job_removed else ' хотела удалить напоминания'


def unset_user(chat_id, mode=True):
    # Удаляет все напоминания юзера
    read_user()
    user_id, lessons_user, nametable = chat_id, user_list[chat_id]['lessons'], user_list[chat_id]['nametimetable']
    for day in table_list[nametable]:
        for lesson in day[1:]:
            time = lesson[1].split(' ')[0]
            unset(chat_id, warning(lesson[2], time))
            unset(chat_id, start_lesson(lesson[2]))
    name = user_list[chat_id]['nametimetable']
    if mode:
        add_user(chat_id, name, [])
    print('!!', chat_id, '- удадил все напоминания')


def set_lessons_user(user):
    read_user()
    user_id, lessons_user, nametable = user, user_list[user]['lessons'], user_list[user]['nametimetable']
    minutes = int(user_list[user]['minut_do'])
    # print(user_id, lessons_user, nametable)
    # print(table_list[nametable])
    now = datetime.now()
    if lessons_user:
        if nametable in table_list.keys():
            for day in table_list[nametable]:
                date = datetime.strptime(day[0], '%d.%m.%Y')
                for lesson in day[1:]:
                    choices = lesson[2].split(';')
                    for choice in choices:
                        predmet = choice.split(' Лк')[0].split(' Пз')[0].split(' Екз')
                        if set(predmet) & set(lessons_user):
                            time = lesson[1].split(' ')[0]
                            time1 = datetime.strptime(time, '%H:%M')
                            t = datetime(date.year, date.month, date.day, time1.hour, time1.minute, 0, 0)
                            if (t > now):
                                # if not job_if_exists(str(user) + ':' + warning(choice.lstrip(), time)):
                                #     if not job_if_exists(str(user) + ':' + start_lesson(choice.lstrip())):
                                set_alarm(user_id, t - timedelta(minutes=minutes), warning(choice.lstrip(), time))
                                set_alarm(user_id, t, start_lesson(choice.lstrip()))
            print('Юзеру ' + str(user) + ':' + str(user_list[user]['nic']) + ' задали напоминания')
        else:
            print(
                'Ошибка, юзеру ' + str(user) + ':' + str(user_list[user]['nic']) + ' не были заданы задали напоминания')


def set_lessons_users():
    # Задает напоминания юзера по выбранным предметам
    try:
        read_user()
        for user in user_list:
            print(user, user_list[user])
        for user in user_list:
            set_lessons_user(user)
        print('!! Все напоминания заданы')
    except:
        print('!! ОШИБКА В ЗАДАНИИ НАПОМИНАНИЙ')


def loging(update, answer, reply_markup=None):
    # выводит переписку в консоль + отправляет смс юзеру
    if not if_get_tables:
        answer += '\n\nТехнические шоколадки... сайт https://cist.nure.ua/ лежит, я тоже...'
    update.message.reply_text(answer, reply_markup=reply_markup)
    print(update.effective_user.mention_markdown_v2(), update.message.from_user.id, update.message.from_user.name)
    print('-', update.message.text.replace('\n', '\\n'))
    print('-', answer.replace('\n', '\\n'), '\n')


def admin_sms(text):
    updater.bot.sendMessage(chat_id=admin, text=text)


def start(update: Update, _: CallbackContext) -> None:
    # стартовая команда для юрера
    answer = 'Привет, я - бот который поможет тебе не забыть о таком важном деле, как отметиться на паре!\n' \
             'Пока что я работаю только с группой ИТКН-18-7,8,9, ИТШИ-1,2 и 7 семестром, но могу расшириться со временем.\n' \
             'Всё что тебе нужно что бы начать со мной работать это нажать на /go.\n\n' \
             'Если ты пропустил все этапы go, то объясняю:\n\n' \
             '/start - я помогу тебе понять зачем меня создали\n\n' \
             '/go - начать работу с напоминаниями для Вас.\nТут я расскажу что нажимать.\n\n' \
             '/gr - нужно, что бы указать группу в который Вы учитесь.\nПравильный формат: "/gr ІТШІ-18-1"\n\n' \
             '/set - нужно, что бы установить какие предметы тебе нужно напоминать.\n' \
             'Номера предметов ты узнаешь из /gr.\n' \
             'Правильный формат: "/set 1 2 3 6"\n\n' \
             '/time - нужно, что бы установить за сколько минут до пары мне нужно напомнить Вам о паре.\n' \
             'По умолчнию стоит 5 минут\n\n' \
             '/check - показывает предметы, о которых вы получаете напоминания\n\n' \
             '/unset - удаляет из напоминаний все выбранные вами предметы, необходимо на случай если вы хотите ' \
             'поменять список своих напоминаемых предметов\n\n' \
             '/next - показывает какой предмет будет следующим по напоминанию.\n' \
             'Можно указать количество следующих предметов \n(например "/next 5" - покажет 5 следующих пар)'
    loging(update, answer, markup)


def go(update: Update, _: CallbackContext) -> None:
    # дает укаазания юзеру: как выбрать свою группу
    answer = 'Отлично, давай начнем!\nЯ знаю расписание групп ІТШІ-18-1,2 и ІТКН-18-7,8,9.\n' \
             'Для начала выбери одну из следующих групп:'
    temp_keyboard = [[], []]

    for gr, i in zip(groups, range(0, len(groups))):
        if i < len(groups) / 2:
            temp_keyboard[0].append('/gr ' + gr)
        else:
            temp_keyboard[1].append('/gr ' + gr)
        # 'Для начала тебе нужно указать свою группу, отправь мне "/gr ІТКН-18-9" - если ты учишься в ней, ' \
        # 'иначе поменяй название на свою группу(пиши на укр)'
    temp_keyboard[1].append('/cancel')
    temp_markup = ReplyKeyboardMarkup(temp_keyboard, one_time_keyboard=False)
    loging(update, answer, temp_markup)
    # get_timetables()


def gr(update: Update, context: CallbackContext) -> None:
    # дает укаазания юзеру: как выбрать предметы
    if context.args:
        group = context.args[0]
        if set(group.split()) & set(groups):
            answer = 'Отлично, значит ты из группы ' + group + \
                     '\nТеперь скажи о каких предметах ты хотешь получать уведомления\n\n' \
                     'Вот номера и названия твоих предметов:\n\n'
            add_user(update.message.from_user.id, group, [], update.message.from_user.name)
            a = 1
            for pr in predmets[group]:
                lector = pr['lector'] if pr['lector'] else ' '
                answer += str(a) + ' - ' + pr['short_name'].replace('*', '') + ', ' + lector + '\n'
                a += 1
            answer += '\nОтправь мне "/set " и номера (через пробел) - тех предметов, ' \
                      'про которые мне надо напомнить Вам (к примеру: "/set 1 2 4")'
            loging(update, answer, markup)
        else:
            answer = 'Я не знаю такой группы, давай я перечислю тебе те, которые знаю:\n'
            for group in groups:
                answer += group + '\n'
            loging(update, answer)
    else:
        answer = 'Ошибочка. Тебе нужно указать группу, в которой ты учишься.\n' \
                 'Отправь мне "/gr (имя группы на укр.)"\n' \
                 'Вот как правильно: "/gr ІТКН-18-9"\n\n' \
                 'Группы, которые я знаю:\n'
        for group in groups:
            answer += group + '\n'
        loging(update, answer)


def unset_predmet(update: Update, _: CallbackContext) -> None:
    # Команда, вызывающая удаление всех напоминанй юзера
    try:
        unset_user(update.message.chat_id)
        answer = 'Вы удалили все напоминания. Если хотите что бы я снова уведомлял вас, пишите /go'
        loging(update, answer)
    except:
        answer = 'Вам нечего удалять. Если хотите что бы я начал вам напоминать про пары, нажмите /go'
        loging(update, answer)


def set_predmet(update: Update, context: CallbackContext) -> None:
    # Команда, определяющая напоминания о каких предметах хочет получать юзер
    unset_user(update.message.chat_id)
    try:
        args = context.args
        group = user_list[update.message.chat_id]['nametimetable']
        if context.args:
            if is_number(args):
                predmets_remind = []
                answer = 'Запомнил!\nПредметы которые будут напоминаться:\n'
                for num in args:
                    if int(num) - 1 < len(predmets[group]) and int(num) > 0:
                        predmets_remind.append(predmets[group][int(num) - 1]['short_name'].replace('*', ''))
                        answer += predmets_remind[-1] + '\n'
                    else:
                        answer = 'Такого номера нет, проверь в списке...'
                        loging(update, answer)
                        update.message.reply_text(answer)
                        return
                add_user(update.message.from_user.id, group, predmets_remind, update.message.from_user.name)
                set_lessons_user(update.message.chat_id)
                loging(update, answer)
                print('!! Пользователь задал себе предметы:', update.message.chat_id, group, predmets_remind)

        else:
            answer = 'Вы не перечислили номера предметов...\n' \
                     'Что бы узнать список ваших предметов нажмите /go'
            loging(update, answer)
    except:
        print('!! ОШИБКА В ЗАДАНИИ ПРЕДМЕТОВ, НЕТ ДАННЫХ О ПРЕДМЕТАХ')
        answer = 'Данные из сайта расписаний не вышло получить...'
        loging(update, answer)


def set_time_do(update: Update, context: CallbackContext) -> None:
    # Команда задающая за сколько юзеру придет напоминание о паре
    if context.args:
        m = context.args[0]
        if is_number(m):
            apd_user(update.message.chat_id, m)
            answer = 'Вы успешно изменили время уведомления! Теперь напоминания будут приходить за: ' + m + ' мин.'
            # set_lessons_user(update.message.chat_id)
            loging(update, answer, markup)
    else:
        answer = 'Эта команда нужна чтобы изменить время, за сколько ' \
                 'тебя нужно уведолмять до начала пары\n\n' \
                 'Введите "/time" и количество минут, за сколько хотите получасть смс ' \
                 '\n(к примеру /time 15)\n\n' \
                 'По умолчанию стоит ' + str(minut_do) + ' минут'
        temp_keyboard = [['/time 3', '/time 5', '/time 7'], ['/time 10', '/time 15', '/cancel']]
        temp_markup = ReplyKeyboardMarkup(temp_keyboard, one_time_keyboard=False)
        loging(update, answer, temp_markup)


def update_table():
    try:
        update_users_un()
        update_users_dw()
        get_timetables()
        set_lessons_users()
        return True
    except:
        return False


def next_cmd(update: Update, context: CallbackContext) -> None:
    user = update.message.chat_id
    text, n, m = '', 0, 1
    if context.args:
        if context.args[0].isdecimal():
            m = int(context.args[0])
    list_j = context.job_queue.jobs()
    print(datetime.now())
    uts = get_uts()
    for l in list_j:
        if l.name.find(str(user)) != -1 and l.name.find('отметься') != -1 and n < m:
            if n == 0:
                now = datetime.today()
                d1 = (now + timedelta(hours=uts)).strftime("%M.%H.%d.%m.%Y")
                d2 = (l.next_t + timedelta(hours=uts)).strftime("%M.%H.%d.%m.%Y")
                d1 = datetime.strptime(d1, "%M.%H.%d.%m.%Y")
                d2 = datetime.strptime(d2, "%M.%H.%d.%m.%Y")
                d = d2 - d1
                print(d.days, d.seconds)
                text += 'До ближайшей пары ' + str(d2 - d1) + '\n'

            date = str(l.next_t.day) + '.' + str(l.next_t.month) + '.' + str(l.next_t.year)
            time = str(l.next_t.hour + uts) + ':' + str(l.next_t.minute)
            text += date + ' ' + time + ' - ' + l.name.split('\n')[1] + '\n'
            n += 1
            # print(l.name.split('\n')[1], l.next_t, l.name.split('\n')[2])
    if text == '':
        text = 'Вы еще не имеете ни одного выбраного предмета для напоминаний!\nИспользуйте /go'
    loging(update, text)


def update_cmd(update: Update, _: CallbackContext) -> None:
    if update_table():
        answer = 'Расписание обновлено.'
        loging(update, answer)
    else:
        answer = 'В обновлении произошла ошибка.'
        loging(update, answer)


def check(update: Update, _: CallbackContext) -> None:
    read_user()
    answer = 'Вы еще не имеете ни одного выбраного предмета для напоминаний!\nИспользуйте /go'
    try:
        list_lessons = user_list[update.message.chat_id]['lessons']
        if list_lessons:
            answer = 'Ваши выбраные предметы:\n' + '\n'.join(list_lessons)
            loging(update, answer)
        else:
            loging(update, answer)
    except:
        loging(update, answer)


def command(_: Update, context: CallbackContext) -> None:
    args = context.args
    if args:
        for com in args:
            try:
                exec(com)
            except:
                print('Попытка вызвать несуществующую функцию: ' + com)


def restart(update: Update, _: CallbackContext) -> None:
    answer = 'Начинаю обновление данных'
    loging(update, answer, markup)
    upd(True)


def read_tables_file(update: Update, _: CallbackContext) -> None:
    # стартовая команда для юрера
    file = open('timetables.txt', 'r', encoding='cp1251')
    answer = file.read()
    file.close()
    if len(answer) > 4096:
        for x in range(0, len(answer), 4096):
            loging(update, answer[x:x + 4096], markup)
    else:
        loging(update, answer, markup)


def read_users_file(update: Update, _: CallbackContext) -> None:
    # стартовая команда для юрера
    file = open('users.txt', 'r', encoding='cp1251')
    answer = file.read()
    file.close()
    loging(update, answer, markup)


def print_users(update: Update, _: CallbackContext) -> None:
    answer = ''
    for user in user_list:
        answer += str(user) + ":"
        if 'nic' in user_list[user].keys():
            if user_list[user]['nic']:
                answer += user_list[user]['nic'] + '\n'
            else:
                answer += 'None' + '\n'
        answer += "Группа: " + user_list[user]['nametimetable'] + '\n'
        answer += "Предметы: "
        for predm in user_list[user]['lessons']:
            answer += predm + ', '
        answer += "\n" + "Время напоминания: " + user_list[user]['minut_do'] + '\n\n'
    loging(update, answer, markup)


def set_admin_keyboard(update: Update, _: CallbackContext) -> None:
    temp_keyboard = [['/rest', '/rt', '/ru', '/pu', '/cancel']]
    temp_markup = ReplyKeyboardMarkup(temp_keyboard, one_time_keyboard=False)
    loging(update, 'Режим админа', temp_markup)


def cancel(update: Update, _: CallbackContext) -> None:
    answer = 'Отмена действий'
    loging(update, answer, markup)


def echo(update: Update, _: CallbackContext) -> None:
    # Основной читалель смс от юзера
    answer = generate_answer(update.message.text)
    loging(update, answer, markup)


print('Start')
print(datetime.now())

cloudinary.config(
    cloud_name=bot_token.cloud_name,
    api_key=bot_token.api_key,
    api_secret=bot_token.api_secret
)

# update_users_dw()
# urllib.request.urlretrieve(file_users, 'users.txt')

try:
    updater = Updater(bot_token.token)
    dispatcher = updater.dispatcher
    reply_keyboard = [['/start', '/go', '/time'], ['/next 10', '/check', '/unset']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    upd()
    if not if_get_tables:
        admin_sms('Проблема с цистом, бот будет обновляться раз в пол часа')

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("go", go))
    dispatcher.add_handler(CommandHandler("gr", gr))
    dispatcher.add_handler(CommandHandler("next", next_cmd))
    dispatcher.add_handler(CommandHandler("check", check))
    dispatcher.add_handler(CommandHandler("update", update_cmd))
    dispatcher.add_handler(CommandHandler("set", set_predmet))
    dispatcher.add_handler(CommandHandler("unset", unset_predmet))
    dispatcher.add_handler(CommandHandler("time", set_time_do))
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    dispatcher.add_handler(CommandHandler("kate", set_admin_keyboard))
    dispatcher.add_handler(CommandHandler("com", command))
    dispatcher.add_handler(CommandHandler("rest", restart))
    dispatcher.add_handler(CommandHandler("rt", read_tables_file))
    dispatcher.add_handler(CommandHandler("ru", read_users_file))
    dispatcher.add_handler(CommandHandler("pu", print_users))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()
except Exception as err:
    admin_sms('БОТ СЛОМАЛСЯ, ИДИ ЧИНИТЬ\n' + str(err))
    print(err)

'''
git add .
git commit -am "make it better"
git push heroku master
heroku ps:scale worker=1

heroku logs -n 1500
'''
