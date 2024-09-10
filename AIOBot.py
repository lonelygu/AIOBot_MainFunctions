from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import Message, BotCommand, BotCommandScopeDefault, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters import Command, Filter
from datetime import datetime

from studentparcer import students
from teacherparcer import teacher
from space import *
from telegramtoken import *

import asyncio
import aiofiles

start_time = datetime.now()
user_states = {}
last_message_times = {}
group = None  # group index
router = Router()


# class Lastname(StatesGroup):
#     lastname = State()
class DepartmentsKeyFilter(Filter):
    def __init__(self, DepartmentsKey_list: list) -> None:
        self.DepartmentsKey_list = DepartmentsKey_list

    async def __call__(self, message: types.Message) -> bool:
        return message.text in self.DepartmentsKey_list

    def get_index(self, message: types.Message) -> int:
        return self.DepartmentsKey_list.index(message.text)


class SurnameFilter(Filter):
    def __init__(self, SurnameFilter_list: list) -> None:
        self.SurnameFilter_list = SurnameFilter_list

    async def __call__(self, message: types.Message) -> bool:
        return message.text in self.SurnameFilter_list


class NotGPTFilter(Filter):
    def __init__(self, condition: bool):
        self.condition = condition

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        user_state = user_states.get(user_id, {})
        return user_state.get('selected_option') != 'GPT'


DepartmentsKey_filter = DepartmentsKeyFilter(DepartmentsKey)


# Commands
async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command="start",
            description="Начало работы",

        ),
        BotCommand(
            command="reboot_date",
            description="Время последнего перезапуска",
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Buttons_common
def button_builder(Button):
    keyboard_builder = ReplyKeyboardBuilder()
    for button_name in Button:
        keyboard_builder.button(text=button_name)
    return keyboard_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def department():
    keyboard_builder = ReplyKeyboardBuilder()
    for x in range(len(DepartmentsKey)):
        keyboard_builder.button(text=DepartmentsKey[x])
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def teachersurname(index: int):
    keyboard_builder = ReplyKeyboardBuilder()
    for x in range(len(Departments[index])):
        keyboard_builder.button(text=Departments[index][x])
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# Buttons_inline
def inline_groups():
    keyboard_builder = InlineKeyboardBuilder()
    for x in range(len(GroupsAll)):
        keyboard_builder.button(text=GroupsAll[x], callback_data=GroupsAll[x])
    keyboard_builder.adjust(4)
    return keyboard_builder.as_markup()


def inline_days():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="<<<", callback_data="left")
    keyboard_builder.button(text=">>>", callback_data="right")
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


# Prosses
async def get_start(message: Message, bot: Bot):
    chat_id = message.from_user.id
    await add_chat_id_to_file(chat_id)
    await set_commands(bot)
    await asyncio.sleep(0.5)
    await message.answer(f"Здравствуйте {message.from_user.first_name}",
                         reply_markup=button_builder(["Расписание", "Питание"]))


async def get_rebootdate(message: Message, bot: Bot):
    chat_id = message.from_user.id
    await add_chat_id_to_file(chat_id)
    await set_commands(bot)
    await asyncio.sleep(0.5)
    reboot_date = start_time.strftime("%d.%m.%Y %H:%M:%S")
    await message.answer(f"Дата последней перезагрузки бота\n<b><i>{reboot_date}</i></b>", parse_mode='HTML')

    warning = await message.answer(
        f"<b><i>Эта команда создана для того, чтобы определить момент времени, когда происходит сброс данных, введенных в бота</i></b>",
        parse_mode='HTML')
    await asyncio.create_task(delete_message_after_delay(bot, chat_id, warning.message_id))


async def delete_message_after_delay(bot: Bot, chat_id: int, message_id: int, delay=5):
    await asyncio.sleep(delay)
    await bot.delete_message(chat_id, message_id)

async def Food_time(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = message.from_user.id
    user_states[user_id] = {'selected_option': 'Питание'}
    await message.answer("10:30\nЭ11-24,Б11-24,Б12-24,Б13-24,Ф11-24\n\n"
                         "10:40\nИС11-24,ИС12-24,ИС13-24,ИС14-24,ИС15-24\n\n"
                         "12:20\nИС16-24,СА11-24,СА12-24,Ф12-24,ИС23-23,Ф13-24\n\n"
                         "12:30\nИБ11-24,ИБ12-24,ИБ13-24,БА11-24,БА13-24\n\n"
                         "14:10\nИС21-23,ИС22-23,ИС24-23,ИС31-22,ИС31-22,СА22-23\n\n"
                         "14:20\nСА21-23,СА31-22,ИБ21-23,ИБ22-23,ИС33-22\n\n"
                         "16:00\nСА41-21,ИБ31-22,ИБ32-23,ИБ41-22,ИБ42-21,БА21-23\n\n"
                         "16:10\nБА23-23,БА31-22,БА32-22,БА41-21,БА42-21\n\n")
    warning = await message.answer(
        f"<b><i>Сделано по просьбе пользователей,в дальнейшем будет дополнено</i></b>",
        parse_mode='HTML')
    await asyncio.create_task(delete_message_after_delay(bot, user_id, warning.message_id))
async def Qualification(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = message.from_user.id
    user_states[user_id] = {'selected_option': 'Расписание'}
    await message.answer("Выберите вашу должность", reply_markup=button_builder(["Студент", "Преподаватель"]))


async def gpt_selection(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_states[user_id] = {'selected_option': 'GPT'}
    await message.answer(f"Вы можете написать любой вопрос для GPT")


async def Group(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    await message.answer("Выберите группу", reply_markup=inline_groups())


async def handle_role_selection(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    role = message.text.lower()
    if role == 'студент':
        # Обработка выбора роли "студент"
        await Group(message, bot)
    elif role == 'преподаватель':
        # Предложение выбрать кафедру
        await message.answer("Выберите вашу Кафедру", reply_markup=department())


async def select_department(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    department_name = message.text
    department_index = DepartmentsKey.index(department_name)
    # Call teachersurname with await to get the keyboard markup
    keyboard_markup = await teachersurname(department_index)
    await message.answer("Выберите преподавателя", reply_markup=keyboard_markup)


async def Sunset(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = message.from_user.id
    user_states[user_id] = {'surname': message.text}
    await message.answer(f"Выберите день", reply_markup=button_builder(["Вчерашний", "Сегодняшний", "Завтрашний"]))


async def bugs(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    await message.answer(f"lonelygu багов найдено ≈ около inf\n@FedyaNev багов найдено = 2\n@zibi14 багов найдено = 1")

# wide-ranging functions
async def Work(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = message.from_user.id
    day = message.text.lower()
    # Извлекаем выбранную группу для пользователя
    selected_group = user_states[user_id]['group']
    if not selected_group:
        await message.answer("Выберите группу перед просмотром расписания.", reply_markup=inline_groups())
        return
    lessons = students(day, selected_group)
    if lessons is not None:
        await message.answer(f"Вот расписание для группы {selected_group} на выбранный вами день")
        await message.answer(f"`{lessons}`", parse_mode='Markdown')
    else:
        await message.answer(f"Расписание для группы {selected_group} на выбранный вами день не было выложено")


async def Tlessons(message: Message, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = message.from_user.id
    secondname = user_states.get(user_id, {}).get('surname', None)
    if not secondname:
        await message.answer("Пожалуйста, выберите преподавателя перед просмотром расписания.",
                             reply_markup=department())
        return

    selected_day = message.text.lower()
    lessons = teacher(selected_day, secondname)
    if lessons is not None:
        await message.answer(f"`{lessons}`", parse_mode='Markdown')
    else:
        await message.answer(f"У данного преподователя нету пар на выбранный вами день")


async def process_callback_button(callback_query: CallbackQuery, bot: Bot):
    await asyncio.sleep(0.5)
    user_id = callback_query.from_user.id
    button = callback_query.data
    if button in ("left", "right"):
        # Update the day selection
        if user_id not in user_states:
            user_states[user_id] = {'group': None, 'day': 0}
        if button == "left":
            user_states[user_id]['day'] = (user_states[user_id]['day'] - 1) % 3
        elif button == "right":
            user_states[user_id]['day'] = (user_states[user_id]['day'] + 1) % 3

        # Determine the day based on the updated state
        if user_states[user_id]['day'] == 0:
            day = "вчера"
        elif user_states[user_id]['day'] == 1:
            day = "сегодня"
        else:
            day = "завтра"

        # Check if a group has been selected
        if user_states[user_id]['group'] is not None:
            result = students(day, user_states[user_id]['group'])
            if result is None:
                result = f"Расписания для группы {user_states[user_id]['group']} на выбранный день - {day},не было выложено"
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=f"`{result}`", reply_markup=inline_days(), parse_mode='Markdown')
        else:
            result = "Вы не выбрали группу"
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=result, reply_markup=inline_groups())
    elif button in GroupsAll:
        # If a group is selected, update the user's state
        user_states[user_id] = {'group': button, 'day': 0}
        await callback_query.answer(f"Вы выбрали группу: {button}")
        # Edit the previous message to display "Выберите день" and the inline keyboard for day selection
        await callback_query.bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=f"Выберите день для группы {button}",
            reply_markup=inline_days()  # This function returns the inline keyboard with arrows
        )


# Multi-user Data Handling Functions
async def add_chat_id_to_file(chat_id):
    file_name = 'chat_ids.txt'
    try:
        # Проверяем, существует ли chat_id в файле
        async with aiofiles.open(file_name, mode='r') as file:
            lines = await file.readlines()
            if f"{chat_id}\n" in lines:
                return

        # Если chat_id не найден, добавляем его в файл
        async with aiofiles.open(file_name, mode='a') as file:
            await file.write(f"{chat_id}\n")
    except Exception as e:
        print(f"Ошибка при записи chat_id в файл: {e}")


# main
async def start():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.message.register(get_start, Command(commands=["start"]))  # Add GPT later to builder
    dp.message.register(get_rebootdate, Command(commands=["reboot_date"]))
    dp.message.register(Food_time, F.text == "Питание")
    dp.message.register(Qualification, F.text == "Расписание")
    dp.message.register(bugs,  F.text.in_(["bugs"]))
    dp.message.register(handle_role_selection, F.text.in_(["Студент", "Преподаватель"]))
    dp.message.register(select_department, DepartmentsKey_filter)
    dp.message.register(Sunset,SurnameFilter(surname))
    dp.callback_query.register(process_callback_button, F.data.in_(GroupsAll))
    dp.callback_query.register(process_callback_button, F.data.in_(["left", "right"]))
    dp.message.register(Work,  F.text.in_(["Вчера", "Сегодня", "Завтра"]))
    dp.message.register(Tlessons, F.text.in_(["Вчерашний", "Сегодняшний", "Завтрашний"]))
    try:
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])
    except asyncio.exceptions.CancelledError:
        print("Программа завершена")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
