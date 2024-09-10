import cloudscraper
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from space import *

CACHE_EXPIRY_SECONDS = 3600
cache_dict = {}
site = 'https://raspmoskbt.ru/rasp/'


def convert(date):
    date_str = date.strftime('%Y-%m-%d')
    year, mouth, day = date_str.split('-')
    ditails = mouths[mouth]
    scary = f"{day}{ditails}{year}"
    return (scary)


def process_table(tables, name):
    if not tables:
        print("Таблиц не найдено.")
        return
    answer = []
    cache = []
    for table in range(len(tables)):
        pattern = re.compile(r'^' + re.escape(name) + r'\b', re.IGNORECASE)
        rows_data = []
        rows = tables[table].find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            row_data = [ele.text.strip().replace('\n', ' ').replace('\xa0', '') for ele in cols]
            rows_data.append(row_data)
        massive = []
        for i, row_data in enumerate(rows_data, start=1):
            massive.append(row_data)
            massive.append([])
        massive = list(filter(None, massive))

        for k in range(len(massive)):
            row_string = ' '.join(str(item) for item in massive[k])
            result = re.findall(name, row_string)
            if result:
                all_indices = [index for index, item in enumerate(massive[k]) if name in item]
                if len(result) > 1:
                    # Если имя встречается более одного раза, добавляем информацию о сдвоенной паре
                    # Используем генератор списка для извлечения всех соответствующих элементов
                    found_items = [massive[k][index] for index in all_indices]
                    moment = datetime.now().date()
                    day_of_week = moment.weekday()
                    if day_of_week == 0:
                        names = [massive[0][index+1] for index in all_indices]
                    else:
                        names = [massive[0][index] for index in all_indices]
                    answer.append(f"Пара {k} будет сдвоенна: {', '.join(found_items)} Для групп {', '.join(names)}")
                else:
                    # Иначе, добавляем информацию о найденной паре
                    found_items = [massive[k][index] for index in all_indices]
                    names = [massive[0][index] for index in all_indices]
                    # Преобразование списка в строку, разделяя элементы запятой и пробелом
                    found_items = ', '.join(found_items) + " c группой " + ', '.join(names)
                    answer.append(f"Пара {k} будет {found_items}")


    if not answer:
        return None
    day = []

    for x, answer_value in enumerate(answer):
        for i, name in enumerate(schedule_name):
            namepattern = re.compile(name)
            tab = " "
            tabpattern = re.compile(tab)
            if i < len(full_name):
                answer_value = re.sub(namepattern, '', answer_value)
                answer_value = re.sub(tabpattern, ' ', answer_value)
        # Добавление значения answer_value в список
        day.append(str(answer_value))
    for x in range(1,6):
        for y in range(len(day)):
            if int(day[y][5]) == x:
                cache.append(day[y])

    cache = '\n\n'.join(cache)

    return cache



def teacher(day,name):
    current = "15aprelya2024"
    moment = datetime.now().date()
    yesterday = today = tomorrow = moment
    day_of_week = moment.weekday()
    if day_of_week not in (0, 4, 5, 6):
        yesterday = moment - timedelta(days=1)
        today = moment
        tomorrow = moment + timedelta(days=1)
    elif day_of_week in (4, 5, 6):
        yesterday = moment - timedelta(days=(day_of_week - 3))
        today = moment - timedelta(days=(day_of_week - 4))
        tomorrow = moment + timedelta(days=(7 - day_of_week))
    elif day_of_week == 0:
        yesterday = moment - timedelta(days=3)
        today = moment
        tomorrow = moment + timedelta(days=1)

    if day == "вчерашний":
        current = convert(yesterday)
    elif day == "сегодняшний":
        current = convert(today)
    elif day == "завтрашний":
        current = convert(tomorrow)
    cache_key = f"{day}_{name}"

    if cache_key in cache_dict and (time.time() - cache_dict[cache_key]['timestamp']) < CACHE_EXPIRY_SECONDS:
        return cache_dict[cache_key]['data']
    else:
        url = site + str(current)
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.yandex.ru/'
        })
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            cell = process_table(tables, name)
            cache_dict[cache_key] = {'data': cell, 'timestamp': time.time()}
            return cell
        else:
            error = ("Ошибка при получении страницы:", response.status_code)
            return error