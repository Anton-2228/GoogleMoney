import GlobalVariables
from SaveChanges import saveData
from Spreadsheet import Spreadsheet
from commands.Synchronize import Synchronize


class DeleteRecord:

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

        count = userData["countIncome"] + userData["countCost"] + 1
        #scope = f'{userData["currentMonth"]}!A{count}:F{count}'
        scope = f'{userData["currentMonth"]}!A2:F{count}'
        values = Spreadsheet.getValues(data[str(message.from_user.id)]["spreadsheetID"], scope)
        if "values" in values:
            for x, z in enumerate(values["values"]):
                if x == len(values['values'])-1 and z[0] != message.get_args() and message.get_args() != "":
                    await message.answer("Операции с таким id нет.")
                    break
                if z[0] == message.get_args() or x == len(values['values'])-1:
                    category = None
                    for i in userCategories:
                        #if userCategories[i]['active'] == '1' and z[3].lower() in userCategories[i]['associations']:
                        if userCategories[i]['active'] == '1' and z[3].lower() == userCategories[i]['name'].lower():
                            category = i
                            if userCategories[i]['income'] == '1':
                                userData['countIncome'] -= 1
                                userData['incomeCategories'][i][0] -= int(z[2])
                                userData['incomeCategories'][i][1][str(userData["actualDay"])] -= int(z[2])
                            else:
                                userData["countCost"] -= 1
                                userData["costCategories"][i][0] += int(z[2])
                                userData["costCategories"][i][1][str(userData["actualDay"])] += int(z[2])
                            break

                    source = None
                    for i in userSources:
                        #if userSources[i]['active'] == '1' and z[5].lower() in userSources[i]['associations']:
                        if userSources[i]['active'] == '1' and z[5].lower() == userSources[i]['name'].lower():
                            source = i
                            if category != None:
                                userData['sources'][i] -= int(z[2])
                            break

                    del userRecords[z[0]]
                    if z[0] == message.get_args():
                        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{userData["currentMonth"]}!A{x+2}:F{x+2}')
                    else:
                        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{userData["currentMonth"]}!A{count}:F{count}')
                    sy = Synchronize()
                    await sy.syncRecords(userData, userRecords)
                    await sy.syncTotal(userData, userCategories, userSources)
                    await message.answer("Удаление операции успешно")
                    saveData()
                    break
