import cloudscraper
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from space import *

cell = []
CACHE_EXPIRY_SECONDS = 3600
cache_dict = {}

moment = datetime.now().date()
yesterday = today = tomorrow = moment
day_of_week = moment.weekday()



def convert(date):
    date_str = date.strftime('%Y-%m-%d')
    year, mouth, day = date_str.split('-')
    ditails = mouths[mouth]
    scary = f"{day}{ditails}{year}"
    return (scary)




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

site = 'https://raspmoskbt.ru/rasp/'


def process_table(tables, index, name_of_group):
    global maybe
    if index < len(tables):
        if len(tables) == 7:
            if index >= 3:
                index = index + 1
        table = tables[index]  # Corrected line
        # Извлечение данных из таблицы
        rows = table.find_all('tr')  # Найти все строки в текущей таблице


        # Инициализация списка для хранения данных столбцов
        columns = []
        # Проход по каждой строке таблицы
        for row in rows:
            cols = row.find_all('td')  # Найти все ячейки в строке
            # Извлечение текста из ячеек и добавление его в соответствующий список столбца
            for i, ele in enumerate(cols):
                text = ele.text.strip().replace('\n', ' ').replace('\xa0', '').replace('  ', ' ')
                if i >= len(columns):
                    columns.append([])
                columns[i].append(text)


        # Итерация по элементам второго массива и замена в строке
        for i, name in enumerate(schedule_name):

            # Создание регулярного выражения для поиска неполного имени
            pattern = re.compile(name)
            # Проверяем, что индекс не выходит за пределы списка full_name
            if i < len(full_name):
                # Итерация по каждому элементу в columns и замена
                for row in columns:
                    for j, cell in enumerate(row):
                        row[j] = re.sub(pattern, full_name[i], cell)
            else:
                print(f"Ошибка: нет полного имени для {name}")
        # The rest of your function remains unchanged
        omnifarious = ("1", " 1", " 1 ", "1 ", "2", " 2", " 2 ", "2 ")
        if columns[0][2] not in omnifarious:
            def get_cell(index):
                return columns[index]

            for i in range(len(columns)):
                globals()[f'cell{i + 1}'] = get_cell(i)
                globals()[f'save{i}'] = globals()[f'cell{i + 1}'][2]
            globals()[f'cell{1}'][2] = "1"

            for x in range(len(columns)):
                if x > 0:
                    globals()[f'cell{x + 1}'][2] = globals()[f'save{x - 1}']
            globals()[f'cell{(len(columns))}'].insert(3, globals()[f'save{len(columns) - 1}'])
            for y in range(len(GroupsForTable[index-1])):
                if name_of_group == GroupsForTable[index-1][y]:
                    cell = globals()[f'cell{y + 2}']
                    return cell
        else:
            for y in range(len(columns)):
                if name_of_group.lower() == columns[y][0].lower().replace('\n', ' ').replace(' ', '')[:7]:
                    cell = columns[y]
                    return cell



def students(day, group):
    current = "15marta2024"
    moment = datetime.now().date()
    yesterday = today = tomorrow = moment
    day_of_week = moment.weekday()
    date = moment
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
    if day == "вчера":
        current = convert(yesterday)
        date = yesterday
    elif day == "сегодня":
        current = convert(today)
        date = today
    elif day == "завтра":
        current = convert(tomorrow)
        date = tomorrow
    cache_key = f"{day}_{group}"

    if cache_key in cache_dict and (time.time() - cache_dict[cache_key]['timestamp']) < CACHE_EXPIRY_SECONDS:
        return cache_dict[cache_key]['data']
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
        tables = soup.find_all('table')  # Найти все таблицы на странице
        index = 0
        for x in range(len(GroupsForTable)):
            if group in GroupsForTable[x]:
                index = x
        cell = process_table(tables, index, group)
        if cell is not None:
            massive = f"Рассписание на {date}\n"
            for x in range(len(cell)):
                for name in full_name:
                    # Create a regular expression pattern for the name
                    pattern = re.compile(name)
                    # Replace each occurrence of the name with a newline character before and after it
                    cell[x] = re.sub(pattern, "\n" + name + "\n", cell[x])
                doamassive = cell[x].splitlines()
                if len(doamassive) == 3 and doamassive[2][0] == " ":
                    doamassive[2] = doamassive[2][1:]
                for element in doamassive:
                    massive += element + "\n"
                massive += "\n"
            cache_dict[cache_key] = {'data': massive, 'timestamp': time.time()}
            return massive
        else:
            cache_dict[cache_key] = {'data': cell, 'timestamp': time.time()}
            return cell

    else:
        error = ("Ошибка при получении страницы:", response.status_code)
        return error