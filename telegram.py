import logging
import json
import re
import datetime

import asyncio

import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem, Item
from aiogram.types import BotCommand

from sheetAPIWrapper import Spreadsheet

from synchronize.syncCategories import syncCat
from synchronize.syncSources import syncSour
from synchronize.addRecord import addRecord
from synchronize.syncTotal import syncTotal

API_TOKEN = "секрет"
#logging.basicConfig(level=logging.INFO, filename="logs.log", format="%(asctime)s %(levelname)s %(message)s")
logging.basicConfig(level=logging.INFO)

CREDENTIALS_FILE = 'data/mmmm-376012-d0a58302e867.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                            ['https://www.googleapis.com/auth/spreadsheets',
                                                                             'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
sheetService = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)
driveService = googleapiclient.discovery.build('drive', 'v3', http=httpAuth)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

with open('data/data.json', 'r') as file:
    data = json.loads(file.read())

with open('data/categories.json', 'r') as file:
    categories = json.loads(file.read())

with open('data/sources.json', 'r') as file:
    sources = json.loads(file.read())

daysUntilNextMonth = {1: 31,
                      2: 28,
                      3: 31,
                      4: 30,
                      5: 31,
                      6: 30,
                      7: 31,
                      8: 31,
                      9: 30,
                      10: 31,
                      11: 30,
                      12: 31}

class Events(Helper):
    mode = HelperMode.snake_case

    CHOICE_TABLE_NAME = ListItem()
    SET_EMAIL = ListItem()
    CORRECT_TABLE = ListItem()
    COMFIRM_DELETE = ListItem()

# Добавление человека в bd
@dp.message_handler(commands=['start'])
async def startFunc(message: types.Message):
    if str(message.from_user.id) not in data:
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(Events.SET_EMAIL[0])
        await message.answer("Пришлите почту на домене @gmail")
        data[str(message.from_user.id)] = {}
        categories[str(message.from_user.id)] = {}
        sources[str(message.from_user.id)] = {}
        #await saveData()
    else:
        await message.answer("Таблица уже существует")

# Добавление почты в bd
@dp.message_handler(state=Events.SET_EMAIL[0])
async def setEmail(message: types.Message):
    if re.fullmatch('\w+@gmail.com', message.text) == None:
        await message.answer("Мне почта не нравится, давай другую")
    else:
        data[str(message.from_user.id)]["email"] = message.text
        #await saveData()
        state = dp.current_state(user=message.from_user.id)
        if "spreadsheetID" not in data[str(message.from_user.id)]:
            await message.answer("Напишите название будущей таблицы:")
            await state.set_state(Events.CHOICE_TABLE_NAME[0])
        else:
            Spreadsheet.issueRights(driveService, data[str(message.from_user.id)]["spreadsheetID"], "user", "writer", data[str(message.from_user.id)]['email'])
            await state.reset_state()
            await message.answer("Права добавлены")

@dp.message_handler(state=Events.CHOICE_TABLE_NAME[0])
async def finishCreateTable(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    await message.answer("Подождите, идет создание таблицы")
    title = message.text
    with open('data/title.json', 'r') as file:
        startSheets = json.load(file)
    spreadsheetID = Spreadsheet.createTable(sheetService, startSheets, title)

    data[str(message.from_user.id)]["spreadsheetID"] = spreadsheetID
    data[str(message.from_user.id)]["countIncome"] = 0
    data[str(message.from_user.id)]["countCost"] = 0
    data[str(message.from_user.id)]["incomeCategories"] = {}
    data[str(message.from_user.id)]["costCategories"] = {}
    data[str(message.from_user.id)]["sources"] = {}
    data[str(message.from_user.id)]["categoryID"] = 0
    data[str(message.from_user.id)]["sourceID"] = 0

    currentMonth = datetime.date.today()
    data[str(message.from_user.id)]["currentMonth"] = str(currentMonth)
    delta = datetime.timedelta(days=daysUntilNextMonth[currentMonth.month])
    nextMonth = currentMonth + datetime.timedelta(days=daysUntilNextMonth[currentMonth.month])
    data[str(message.from_user.id)]["nextMonth"] = str(nextMonth)
    data[str(message.from_user.id)]["nextDay"] = str(currentMonth + datetime.timedelta(days=1))

    data[str(message.from_user.id)]["daysCurMonth"] = delta.days
    data[str(message.from_user.id)]["actualDay"] = 0

    with open('data/templates.json', 'r') as file:
        template = json.load(file)
    value = [currentMonth, template["template"]]
    response = Spreadsheet.addNewSheet(sheetService, spreadsheetID, value, delta)

    Spreadsheet.issueRights(driveService, data[str(message.from_user.id)]["spreadsheetID"], "user", "writer", data[str(message.from_user.id)]['email'])
    await saveData()
    counter.create_task(timer(str(message.from_user.id)))
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheetID}/edit#gid=0"
    await message.answer("ссылка на таблицу: " + url)
    await help(message)

@dp.message_handler(commands=["sync"])
@dp.message_handler(state=Events.CORRECT_TABLE[0], commands=["sync"])
async def synchronize(message: types.Message):
    userData = data[str(message.from_user.id)]
    userCategories = categories[str(message.from_user.id)]
    userSources = sources[str(message.from_user.id)]
    resultSyncCat = syncCat(userData, userCategories, sheetService, "Categories!A2:G100000")
    if type(resultSyncCat) == str:
        await message.answer(resultSyncCat)

    resultSyncSour = syncSour(userData, userSources, sheetService, "Bills!A2:E100000")
    if type(resultSyncSour) == str:
        await message.answer(resultSyncSour)

    if resultSyncCat == True:
        await message.answer("Синхронизация категорий успешна")
    if resultSyncSour == True:
        await message.answer("Синхронизация источников успешна")

    state = dp.current_state(user=message.from_user.id)
    if resultSyncSour == True and resultSyncCat == True:
        await state.reset_state()
        Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], 'Categories!A2:G100000')
        Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], 'Bills!A2:E100000')

        values = []

        value = []
        for i in userCategories:
            category = userCategories[i]
            value.append([i, category['active'], category['income'], category['cost'], category['name'], ' '.join(category['associations']), category['limit']])
        values.append(["Categories", "ROWS", f'A2:G{len(userCategories) + 2}', value])

        value = []
        for i in userSources:
            source = userSources[i]
            value.append([i, source['active'], source['name'], ' '.join(source['associations']), source['startBalance']])
        values.append(["Bills", "ROWS", f'A2:F{len(userSources) + 2}', value])

        syncTotal(userData, userCategories, userSources, sheetService)

        Spreadsheet.setValues(sheetService, userData["spreadsheetID"], values)
        await saveData()
    else:
        await state.set_state(Events.CORRECT_TABLE[0])

@dp.message_handler(state=Events.CORRECT_TABLE[0])
async def errorRecord(message: types.Message):
    await message.answer("Исправьте таблицу и синхронизируйте её")

@dp.message_handler(commands=["changeemail"])
async def changeEmail(message: types.Message):
    await message.answer("Пришлите почту на домене @gmail")
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(Events.SET_EMAIL[0])

@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    with open('data/help.txt', 'r', encoding='utf-8') as file:
        await message.answer(file.read())

@dp.message_handler(commands=["table"])
async def getTable(message: types.Message):
    spreadsheetID = data[str(message.from_user.id)]["spreadsheetID"]
    await message.answer(f"Ссылка на таблицу:\nhttps://docs.google.com/spreadsheets/d/{spreadsheetID}/edit#gid=0")

@dp.message_handler(commands=["del"])
async def deleteLastRecord(message: types.Message):
    userData = data[str(message.from_user.id)]
    userCategories = categories[str(message.from_user.id)]
    userSources = sources[str(message.from_user.id)]
    count = userData["countIncome"] + userData["countCost"] + 1
    scope = f'{userData["currentMonth"]}!A{count}:E{count}'
    values = Spreadsheet.getValues(sheetService, data[str(message.from_user.id)]["spreadsheetID"], scope)
    if "values" in values:
        values = values['values'][0]
        category = None
        for i in userCategories:
            if userCategories[i]['active'] == '1' and values[2].lower() in userCategories[i]['associations']:
                category = i
                if userCategories[i]['income'] == '1':
                    userData['countIncome'] -= 1
                    userData['incomeCategories'][i][0] -= int(values[1])
                    userData['incomeCategories'][i][1][str(userData["actualDay"])] -= int(values[1])
                else:
                    userData["countCost"] -= 1
                    userData["costCategories"][i][0] += int(values[1])
                    userData["costCategories"][i][1][str(userData["actualDay"])] += int(values[1])
                break

        source = None
        for i in userSources:
            if userSources[i]['active'] == '1' and values[4].lower() in userSources[i]['associations']:
                source = i
                if category != None:
                    userData['sources'][i] -= int(values[1])
                break

        Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!A{count}:E{count}')
        syncTotal(userData, userCategories, userSources, sheetService)
        await saveData()

@dp.message_handler(commands=["deletetable"])
async def deleteTable(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(Events.COMFIRM_DELETE[0])
    await message.answer("Напишите 'ПОДТВЕРЖДАЮ УДАЛЕНИЕ' для удаления таблицы.\nСама таблица существовать продолжит, однако привязать её к боту будет уже невозможно")

@dp.message_handler(state=Events.COMFIRM_DELETE[0])
async def confirmDelete(message: types.Message):
    text = message.text
    if text != "ПОДТВЕРЖДАЮ УДАЛЕНИЕ":
        await message.answer('Удаление таблицы отменено')
    else:
        del data[str(message.from_user.id)]
        del categories[str(message.from_user.id)]
        del sources[str(message.from_user.id)]
        state = dp.current_state(user=message.from_user.id)
        await state.reset_state()
        await message.answer('Для создания новой таблицы напишите /start')
        await saveData()

#async def timer(message: types.Message):
async def timer(id):
    userData = data[id]
    userCategories = categories[id]
    userSources = sources[id]
    while True:
        today = datetime.date.today()
        if str(today) == userData["nextMonth"]:
            with open('data/templates.json', 'r') as file:
                template = json.load(file)
            values = [str(today), template["template"]]
            Spreadsheet.addNewSheet(sheetService, userData["spreadsheetID"], values)

            userData["currentMonth"] = str(today)
            delta = datetime.timedelta(days=daysUntilNextMonth[today.month])
            nextMonth = today + datetime.timedelta(days=daysUntilNextMonth[today.month])
            userData["nextMonth"] = str(nextMonth)
            userData["nextDay"] = str(today + datetime.timedelta(days=1))
            userData["daysCurMonth"] = delta.days
            userData["actualDay"] = 0

            for i in userData["incomeCategories"]:
                userData["incomeCategories"][i][0] = 0
                userData["incomeCategories"][i][1] = {}
                for z in range(userData["daysCurMonth"]):
                    userData['incomeCategories'][i][1][z] = 0
            for i in userData["costCategories"]:
                userData["costCategories"][i][0] = 0
                userData["costCategories"][i][1] = {}
                for z in range(userData["daysCurMonth"]):
                    userData['costCategories'][i][1][z] = 0
            userData["countCost"] = 0
            userData["countIncome"] = 0
            await saveData()
        elif str(today) == userData["nextDay"]:
        #elif True:
            old = list(map(int, userData["nextDay"].split('-')))
            nextday = datetime.date(year=old[0], month=old[1], day=old[2])
            userData["nextDay"] = str(nextday + datetime.timedelta(days=1))
            userData["actualDay"] += 1
            syncTotal(userData, userCategories, userSources, sheetService)
            await saveData()
        #await asyncio.sleep(120)
        await asyncio.sleep(10)

# сумма категория источник пометка
@dp.message_handler()
async def newRecord(message: types.Message):
    userData = data[str(message.from_user.id)]
    userCategories = categories[str(message.from_user.id)]
    userSources = sources[str(message.from_user.id)]
    args = message.text.split()
    result = addRecord(userData, userCategories, userSources, sheetService, args)
    if type(result) == str:
        await message.answer(result)
    elif type(result) == list:
        await message.answer(result[0])
        for i in userCategories:
            limit = userCategories[i]['limit']
            if args[1].lower() in userCategories[i]['associations'] and limit != '-' and int(limit) < userData['costCategories'][i][0]:
                await message.answer("Превышен установленный лимит на эту категорию")
        await saveData()

async def saveData():
    # Я ЗНАЮ ЧТО ЭТО ПИЗДЕЦ, ВСЕ БУДЕТ ПЕРЕДЕЛАНО
    with open('data/data.json', 'w+') as file:
        json.dump(data, file)
    with open('data/categories.json', 'w+') as file:
        json.dump(categories, file)
    with open('data/sources.json', 'w+') as file:
        json.dump(sources, file)

async def startup(dispatcher: Dispatcher):
    for i in data:
        counter.create_task(timer(i))

async def shutdown(dispatcher: Dispatcher):
    '''
    with open('data/data.json', 'w+') as file:
        json.dump(data, file)
    with open('data/categories.json', 'w+') as file:
        json.dump(categories, file)
    with open('data/sources.json', 'w+') as file:
        json.dump(sources, file)
    '''
    for i in data:
        state = dp.current_state(user=i)
        await state.reset_state()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == "__main__":
    counter = asyncio.get_event_loop()
    executor.start_polling(dp, on_startup=startup, on_shutdown=shutdown)