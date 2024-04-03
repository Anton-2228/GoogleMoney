import re
import datetime

from sheetAPIWrapper import Spreadsheet
from synchronize.syncTotal import syncTotal

def addRecord(userData, userCategories, userSources, sheetService, args):
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
            #value = [sheet, "ROWS", f"A{count}:E{count}", [[str(datetime.date.today()), args[0], userCategories[category]['name'], note, userSources[source]['name']]]]
            #Spreadsheet.setValues(sheetService, data[str(message.from_user.id)]["spreadsheetID"], [value])

            #values = []

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

            values.append([userData["currentMonth"], "ROWS", f"A{count}:E{count}", [[str(datetime.date.today()), amount, userCategories[category]['name'], note, userSources[source]['name']]]])

            Spreadsheet.setValues(sheetService, userData["spreadsheetID"], values)

            syncTotal(userData, userCategories, userSources, sheetService)

            return [f"Сумма {args[0]}\nзаписана как {typeCat} --> {userCategories[category]['name']}\nиз {userSources[source]['name']}\nc пометкой {note}", True]

        #value = ["Bills", "ROWS", f"A{z + 2}:{z + 2}", [[data[str(message.from_user.id)]["sourceID"]]]]
        #Spreadsheet.setValues(sheetService, data[str(message.from_user.id)]["spreadsheetID"], [value])