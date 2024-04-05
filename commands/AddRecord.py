import datetime
import re

import GlobalVariables
from SaveChanges import saveData
from Spreadsheet import Spreadsheet
from commands.Synchronize import Synchronize


class AddRecord:

    def __init__(self):
        global data, categories, sources, records
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        records = GlobalVariables.records

    async def execute(self, message):
        userData = data[str(message.from_user.id)]
        userCategories = categories[str(message.from_user.id)]
        userSources = sources[str(message.from_user.id)]
        userRecords = records[str(message.from_user.id)]

        args = message.text.split()
        result = await self.addRecord(userData, userCategories, userSources, userRecords, args)
        if type(result) == str:
            await message.answer(result)
        elif type(result) == list:
            await message.answer(result[0])
            for i in userCategories:
                limit = userCategories[i]['limit']
                if args[1].lower() in userCategories[i]['associations'] and limit != '-' and int(limit) < userData['costCategories'][i][0]:
                    await message.answer("Превышен установленный лимит на эту категорию")
            saveData()

    async def addRecord(self, userData, userCategories, userSources, userRecords, args):
        if len(args) < 3:
            return "Какой-то странный ввод"
        elif re.fullmatch('\d+', args[0]) == None:
            return "Сумма должна быть натуральным числом"
        else:
            category = None
            for i in userCategories:
                if userCategories[i]['active'] == '1' and args[1].lower() in userCategories[i]['associations']:
                    category = i
                    break
            if category == None:
                return "Такой категории нет, либо она выключена"

            source = None
            for i in userSources:
                if userSources[i]['active'] == '1' and args[2].lower() in userSources[i]['associations']:
                    source = i
                    break
            if source == None:
                return "Такого источника нет, либо он выключен"

            note = ' '.join(args[3:])
            if category != None and source != None:
                # value = [sheet, "ROWS", f"A{count}:E{count}", [[str(datetime.date.today()), args[0], userCategories[category]['name'], note, userSources[source]['name']]]]
                # Spreadsheet.setValues(sheetService, data[str(message.from_user.id)]["spreadsheetID"], [value])

                # values = []

                if userCategories[category]['income'] == '1':
                    typeCat = "доход"
                    userData['countIncome'] += 1
                    userData['incomeCategories'][category][0] += int(args[0])
                    userData['incomeCategories'][category][1][str(userData["actualDay"])] += int(args[0])
                else:
                    typeCat = "расход"
                    userData["countCost"] += 1
                    userData["costCategories"][category][0] += int(args[0])
                    userData["costCategories"][category][1][str(userData["actualDay"])] += int(args[0])
                count = userData["countIncome"] + userData["countCost"] + 1

                if userCategories[category]['income'] == '1':
                    userData['sources'][source] += int(args[0])
                else:
                    userData['sources'][source] -= int(args[0])

                if typeCat == 'доход':
                    amount = f'+{args[0]}'
                else:
                    amount = f'-{args[0]}'

                values = []

                ids = Spreadsheet.getValues(userData["spreadsheetID"], f'{userData["currentMonth"]}!A2:A100000')
                id = 1
                if "values" in ids:
                    ids = list(map(lambda x: x[0], ids["values"]))
                    ids = list(map(int, ids))
                    id = max(ids) + 1

                values.append([userData["currentMonth"], "ROWS", f"A{count}:F{count}", [[id, str(datetime.date.today()), amount, userCategories[category]['name'], note, userSources[source]['name']]]])
                userRecords[str(id)] = [id, str(datetime.date.today()), amount, userCategories[category]['name'], note, userSources[source]['name']]

                Spreadsheet.setValues(userData["spreadsheetID"], values)

                sy = Synchronize()
                await sy.syncTotal(userData, userCategories, userSources)

                return [
                    f"Сумма {args[0]}\n{typeCat} --> {userCategories[category]['name']}\nиз {userSources[source]['name']}\nc пометкой: {note}\nid:{str(id-1)}",
                    True]

            # value = ["Bills", "ROWS", f"A{z + 2}:{z + 2}", [[data[str(message.from_user.id)]["sourceID"]]]]
            # Spreadsheet.setValues(sheetService, data[str(message.from_user.id)]["spreadsheetID"], [value])