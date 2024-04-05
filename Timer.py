import asyncio
import datetime

import GlobalVariables
from SaveChanges import saveData
from Spreadsheet import Spreadsheet
from commands.Synchronize import Synchronize

class Timer():
    def __init__(self):
        global data, categories, sources, records, daysUntilNextMonth
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        records = GlobalVariables.records
        daysUntilNextMonth = GlobalVariables.daysUntilNextMonth

    async def execute(self, id):
        userData = data[id]
        userCategories = categories[id]
        userSources = sources[id]
        userRecords = records[id]
        while True:
            today = datetime.date.today()
            if str(today) == userData["nextMonth"]:
                userData["currentMonth"] = str(today)
                delta = datetime.timedelta(days=daysUntilNextMonth[today.month])
                nextMonth = today + datetime.timedelta(days=daysUntilNextMonth[today.month])
                userData["nextMonth"] = str(nextMonth)
                userData["nextDay"] = str(today + datetime.timedelta(days=1))
                userData["daysCurMonth"] = delta.days
                userData["actualDay"] = 0
                userRecords = {}

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
                #userData["countCost"] = 0
                #userData["countIncome"] = 0
                response = Spreadsheet.addNewOperationsSheet(userData["spreadsheetID"], userData["currentMonth"])
                response = Spreadsheet.addNewStatisticsSheet(userData["spreadsheetID"], userData["currentMonth"], delta)
                saveData()
            elif str(today) == userData["nextDay"]:
                old = list(map(int, userData["nextDay"].split('-')))
                nextday = datetime.date(year=old[0], month=old[1], day=old[2])
                userData["nextDay"] = str(nextday + datetime.timedelta(days=1))
                userData["actualDay"] += 1
                sy = Synchronize()
                await sy.syncTotal(userData, userCategories, userSources)
                saveData()
            #await asyncio.sleep(120)
            await asyncio.sleep(10)