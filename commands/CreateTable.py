import datetime
import re

import GlobalVariables
from SaveChanges import saveData
from Spreadsheet import Spreadsheet


class CreateTable:

    def __init__(self):
        global dp, data, categories, sources, records, Events, startSheets, sheetService, driveService, daysUntilNextMonth, template, commandManager, counter, globTimer
        dp = GlobalVariables.dispatcher
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        records = GlobalVariables.records
        Events = GlobalVariables.Events
        startSheets = GlobalVariables.titles
        sheetService = GlobalVariables.sheetService
        driveService = GlobalVariables.driveService
        daysUntilNextMonth = GlobalVariables.daysUntilNextMonth
        template = GlobalVariables.templateOperatios
        counter = GlobalVariables.counter
        globTimer = GlobalVariables.globTimer

    async def execute(self, message):
        state = dp.current_state(user=message.from_user.id)

        if await state.get_state() == None:

            if str(message.from_user.id) not in data:
                data[str(message.from_user.id)] = {}
                categories[str(message.from_user.id)] = {}
                sources[str(message.from_user.id)] = {}
                records[str(message.from_user.id)] = {}
                await state.set_state(Events.SET_EMAIL[0])
                await message.answer("Пришлите почту на домене @gmail")
            else:
                await message.answer("Таблица уже существует")

        elif await state.get_state() == "set_email":

            if re.fullmatch('\w+@gmail.com', message.text) == None:
                await message.answer("Мне почта не нравится, давай другую")
            else:
                data[str(message.from_user.id)]["email"] = message.text
                state = dp.current_state(user=message.from_user.id)
                await message.answer("Напишите название будущей таблицы:")
                await state.set_state(Events.CHOICE_TABLE_NAME[0])

        elif await state.get_state() == "choice_table_name":

            await state.set_state(Events.COMFIRM_CHANGE_DATE_RESET[0])
            await message.answer("Подождите, идет создание таблицы")
            title = message.text
            spreadsheetID = Spreadsheet.createTable(title, data[str(message.from_user.id)]["email"])
            print(f"https://docs.google.com/spreadsheets/d/{spreadsheetID}/")

            data[str(message.from_user.id)]["spreadsheetID"] = spreadsheetID
            data[str(message.from_user.id)]["countIncome"] = 0
            data[str(message.from_user.id)]["countCost"] = 0
            data[str(message.from_user.id)]["incomeCategories"] = {}
            data[str(message.from_user.id)]["costCategories"] = {}
            data[str(message.from_user.id)]["sources"] = {}

            currentMonth = datetime.date.today()
            data[str(message.from_user.id)]["currentMonth"] = str(currentMonth)
            delta = datetime.timedelta(days=daysUntilNextMonth[currentMonth.month])
            nextMonth = currentMonth + datetime.timedelta(days=daysUntilNextMonth[currentMonth.month])
            data[str(message.from_user.id)]["nextMonth"] = str(nextMonth)
            data[str(message.from_user.id)]["nextDay"] = str(currentMonth + datetime.timedelta(days=1))

            data[str(message.from_user.id)]["daysCurMonth"] = delta.days
            data[str(message.from_user.id)]["actualDay"] = 0

            response = Spreadsheet.addNewOperationsSheet(spreadsheetID, currentMonth)
            response = Spreadsheet.addNewStatisticsSheet(spreadsheetID, currentMonth, delta)

            saveData()
            counter.create_task(globTimer.execute(str(message.from_user.id)))
            await message.answer("Напишите день, в который будет происходить переход таблицы на новый месяц(этот день должен быть в каждом месяце, т.е. меньший 29)")

        elif await state.get_state() == "comfirm_change_date_reset":
            try:
                userData = data[str(message.from_user.id)]
                today = datetime.date.today()
                curDay = userData["currentMonth"].split('-')
                if int(message.text.split()[0]) > 0 and int(message.text.split()[0]) < 29:
                    if int(message.text.split()[0]) > int(curDay[2]):
                        nex = today + datetime.timedelta(days=int(message.text.split()[0])) - datetime.timedelta(days=int(curDay[2]))
                    else:
                        nex = today + datetime.timedelta(days=daysUntilNextMonth[int(curDay[1])]) + datetime.timedelta(days=int(message.text.split()[0])) - datetime.timedelta(days=int(curDay[2]))
                    userData["nextMonth"] = str(nex)
                    saveData()
                    await state.reset_state()

                    url = f"https://docs.google.com/spreadsheets/d/{userData['spreadsheetID']}/edit#gid=0"
                    await message.answer("ссылка на таблицу: " + url)
                    commandManager = GlobalVariables.commandManager
                    await commandManager.getCommands()['help'].execute(message)
                else:
                    await message.answer("Число должно быть > 0 и < 29")
            except:
                await message.answer("Странное число")