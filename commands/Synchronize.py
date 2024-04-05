import copy
import re

import GlobalVariables
from SaveChanges import saveData
from Spreadsheet import Spreadsheet


class Synchronize:

    def __init__(self):
        global dp, data, categories, sources, Events, sheetService
        dp = GlobalVariables.dispatcher
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        Events = GlobalVariables.Events
        sheetService = GlobalVariables.sheetService

    async def execute(self, message):
        userData = data[str(message.from_user.id)]
        userCategories = categories[str(message.from_user.id)]
        userSources = sources[str(message.from_user.id)]

        resultSyncCat = await self.syncCat(userData, userCategories, "Categories!A2:G100000")
        if type(resultSyncCat[0]) == str:
            await message.answer(resultSyncCat)

        resultSyncSour = await self.syncSour(userData, userSources, "Bills!A2:E100000")
        if type(resultSyncSour[0]) == str:
            await message.answer(resultSyncSour)

        values = []

        if type(resultSyncCat[0]) == dict:
            for i in resultSyncCat[0]:
                userCategories[i] = copy.deepcopy(resultSyncCat[0][i])
            for i in resultSyncCat[1]:
                userData['incomeCategories'][i] = copy.deepcopy(resultSyncCat[1][i])
            for i in resultSyncCat[2]:
                userData['costCategories'][i] = copy.deepcopy(resultSyncCat[2][i])
            await message.answer("Синхронизация категорий успешна")

            Spreadsheet.cleanValues(userData["spreadsheetID"], 'Categories!A2:G100000')

            value = []
            for i in userCategories:
                category = userCategories[i]
                value.append([i, category['active'], category['income'], category['cost'], category['name'],
                              ' '.join(category['associations']), category['limit']])
            values.append(["Categories", "ROWS", f'A2:G{len(userCategories) + 2}', value])

        if type(resultSyncSour[0]) == dict:
            for i in resultSyncSour[0]:
                userSources[i] = copy.deepcopy(resultSyncSour[0][i])
            for i in resultSyncSour[1]:
                userData['sources'][i] = copy.deepcopy(resultSyncSour[1][i])
            await message.answer("Синхронизация источников успешна")

            Spreadsheet.cleanValues(userData["spreadsheetID"], 'Bills!A2:E100000')

            value = []
            for i in userSources:
                source = userSources[i]
                value.append(
                    [i, source['active'], source['name'], ' '.join(source['associations']), source['startBalance'], source['currentBalance']])
            values.append(["Bills", "ROWS", f'A2:F{len(userSources) + 2}', value])

        if type(resultSyncSour[0]) == dict or type(resultSyncCat[0]) == dict:
            Spreadsheet.setValues(userData["spreadsheetID"], values)
            saveData()

        state = dp.current_state(user=message.from_user.id)
        if type(resultSyncSour[0]) == dict and type(resultSyncCat[0]) == dict:
            #await message.answer("Синхронизация успешна")
            await state.reset_state()

            # for i in resultSyncCat:
            #     userCategories[i] = copy.deepcopy(resultSyncCat[i])
            # for i in resultSyncSour:
            #     userSources[i] = copy.deepcopy(resultSyncSour[i])

            # Spreadsheet.cleanValues(userData["spreadsheetID"], 'Categories!A2:G100000')
            # Spreadsheet.cleanValues(userData["spreadsheetID"], 'Bills!A2:E100000')

            #values = []

            # value = []
            # for i in userCategories:
            #     category = userCategories[i]
            #     value.append([i, category['active'], category['income'], category['cost'], category['name'], ' '.join(category['associations']), category['limit']])
            # values.append(["Categories", "ROWS", f'A2:G{len(userCategories) + 2}', value])

            # value = []
            # for i in userSources:
            #     source = userSources[i]
            #     value.append([i, source['active'], source['name'], ' '.join(source['associations']), source['startBalance'], source['currentBalance']])
            # values.append(["Bills", "ROWS", f'A2:F{len(userSources) + 2}', value])

            await self.syncTotal(userData, userCategories, userSources)

            # Spreadsheet.setValues(userData["spreadsheetID"], values)
            # saveData()
        else:
            await state.set_state(Events.CORRECT_TABLE[0])

    async def syncCat(self, userData, userCategories, scope):
        cat = Spreadsheet.getValues(userData["spreadsheetID"], scope)
        add = {}
        locIncome = {}
        locCost = {}
        if "values" in cat:
            for z, row in enumerate(cat["values"]):
                print(row)
                if len(row) == 0:
                    continue
                elif len(row) == 1:
                    if userCategories[row[0]]['income'] == '1':
                        del userData['incomeCategories'][row[0]]
                    else:
                        del userData['costCategories'][row[0]]
                    del userCategories[row[0]]
                elif len(row) < 7:
                    return f"В категориях в {z + 1} строке не все поля заполнены"
                elif row[1] not in ['0', '1']:
                    return f"В категориях в {z + 1} строке Active странный"
                elif row[2] not in ['0', '1']:
                    return f"В категориях в {z + 1} строке Income странный"
                elif row[3] not in ['0', '1']:
                    return f"В категориях в {z + 1} строке Cost странный"
                elif row[2] == row[3]:
                    return f"В категориях в {z + 1} строке одинаковое значение у Income и Cost"
                elif row[4] == '':
                    return f"В категориях в {z + 1} строке Name пустой"
                elif len(row[4].split()) > 1:
                    return f"В категориях в {z + 1} строке Name записан не одним словом"
                elif ((row[0] != '' and row[4] != (userCategories | add)[row[0]]['name']) or row[0] == '') and row[4] in list(map(lambda x: (userCategories | add)[x]['name'], list(add)+list(userCategories))):
                    return f"В категориях в {z + 1} строке используется уже существующий Name"
                elif row[6] not in ['', '-'] and re.fullmatch('\d+', row[6]) == None:
                    return f"В категориях в {z + 1} строке Limits должен быть записан натуральным числом, либо, если он отсутствует, дефисом('-')"
                elif row[6] not in ['', '-'] and row[2] == '1':
                    return f"В категориях в {z + 1} строке стоит лимит у категории дохода"
                else:
                    if row[0] != '':
                        userCategories[row[0]]['associations'] = []
                    cross = []
                    #for i in userCategories:
                    for i in add | userCategories:
                        for k in list(set(row[5].split() + [row[4]]).intersection(set((userCategories | add)[i]['associations']))):
                            cross.append(k)
                    if len(cross) != 0:
                        return f"В категориях в {z + 1} строке {', '.join(cross)} использован/ы повторно"
                    else:
                        if row[0] == '':
                            #row[0] = str(userData["categoryID"])
                            id = 1
                            if list(userData["incomeCategories"] | locIncome) + list(userData["costCategories"] | locCost) != []:
                                id = max(list(map(int, list(userData["incomeCategories"] | locIncome) + list(userData["costCategories"] | locCost)))) + 1
                            row[0] = str(id)
                            if row[2] == '1':
                                # userData['incomeCategories'][row[0]] = [0, {}]
                                locIncome[row[0]] = [0, {}]
                                for v in range(int(userData["daysCurMonth"])):
                                    locIncome[row[0]][1][str(v)] = 0
                            else:
                                # userData['costCategories'][row[0]] = [0, {}]
                                locCost[row[0]] = [0, {}]
                                for v in range(userData["daysCurMonth"]):
                                    locCost[row[0]][1][str(v)] = 0
                            #userData["categoryID"] += 1
                        associations = row[5].split() + [row[4]]
                        associations = list(set(map(lambda x: x.lower(), associations)))
                        #userCategories[row[0]] = {"active": row[1], 'income': row[2], 'cost': row[3], 'name': row[4], 'associations': associations, 'limit': row[6]}
                        add[row[0]] = {"active": row[1], 'income': row[2], 'cost': row[3], 'name': row[4], 'associations': associations, 'limit': row[6]}
        return [add, locIncome, locCost]

    async def syncSour(self, userData, userSources, scope):
        sour = Spreadsheet.getValues(userData["spreadsheetID"], scope)
        add = {}
        locSource = {}
        if "values" in sour:
            for z, row in enumerate(sour["values"]):
                print(row)
                if len(row) == 0:
                    continue
                elif len(row) == 1:
                    del userData["sources"][row[0]]
                    del userSources[row[0]]
                elif len(row) < 5:
                    return f"В источниках в {z + 1} строке не все поля заполнены"
                elif row[1] not in ['0', '1']:
                    return f"В источниках в {z + 1} строке Active странный"
                elif row[2] == '':
                    return f"В источниках в {z + 1} строке Name пустой"
                elif ((row[0] != '' and row[2] != (userSources | add)[row[0]]['name']) or row[0] == '') and row[2] in list(map(lambda x: (userSources | add)[x]['name'], list(add) + list(userSources))):
                    return f"В источниках в {z + 1} строке используется уже существующий Name"
                elif len(row[2].split()) > 1:
                    return f"В источниках в {z + 1} строке Name записан не одним словом"
                elif re.fullmatch('-?\d+', row[4]) == None:
                    return f"В источниках в {z + 1} строке Balance должен быть целым числом"
                else:
                    if row[0] != '':
                        userSources[row[0]]['associations'] = []
                    cross = []
                    #for i in userSources:
                    for i in add | userSources:
                        #for k in list(set(row[3].split() + [row[2]]).intersection(set(userSources[i]['associations']))):
                        for k in list(set(row[3].split() + [row[2]]).intersection(set((userSources | add)[i]['associations']))):
                            cross.append(k)
                    if len(cross) != 0:
                        return f"В источниках в {z + 1} строке {', '.join(cross)} использован/ы повторно"
                    else:
                        if row[0] == '':
                            #row[0] = str(userData['sourceID'])
                            id = 1
                            if list(userData['sources'] | locSource) != []:
                                id = max(list(map(int, list(userData['sources'] | locSource)))) + 1
                            row[0] = str(id)
                            # userData['sources'][row[0]] = int(row[4])
                            locSource[row[0]] = int(row[4])
                            #userData["sourceID"] += 1
                        else:
                            delta = int(row[4]) - int(userSources[row[0]]['startBalance'])
                            userData['sources'][row[0]] += delta
                        associations = row[3].split() + [row[2]]
                        associations = list(set(map(lambda x: x.lower(), associations)))
                        #userSources[row[0]] = {"active": row[1], "name": row[2], 'associations': associations, 'startBalance': row[4], 'currentBalance': row[4]}
                        add[row[0]] = {"active": row[1], "name": row[2], 'associations': associations, 'startBalance': row[4], 'currentBalance': (userData['sources'] | locSource)[row[0]]}
        return [add, locSource]

    async def syncTotal(self, userData, userCategories, userSources):
        alf = GlobalVariables.alf
        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{"Stat. " + userData["currentMonth"]}!A2:B100000')
        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{"Stat. " + userData["currentMonth"]}!{alf[userData["daysCurMonth"]]}2:{alf[userData["daysCurMonth"]]}1000')
        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{"Stat. " + userData["currentMonth"]}!A2:{alf[userData["daysCurMonth"]]}1000')
        values = []

        value = []
        totalSumCost = 0
        sumCostDayList = [0]*userData["daysCurMonth"]
        for i in userData['costCategories']:
            totalSumCost += int(userData['costCategories'][i][0])
            value.append([userCategories[i]['name'], userData['costCategories'][i][0]])
            for z in userData['costCategories'][i][1]:
                sumCostDayList[int(z)] += userData['costCategories'][i][1][z]
                value[-1].append(userData['costCategories'][i][1][z])
        value.insert(0, ['Общие расходы', totalSumCost]+sumCostDayList)
        values.append(["Stat. " + userData["currentMonth"], 'ROWS',
                       f'A{len(userData["incomeCategories"]) + 2 + 1 + 1}:{alf[userData["daysCurMonth"]]}{len(userData["incomeCategories"]) + len(userData["costCategories"]) + 2 + 1 + 1}',
                       value])

        sheets = Spreadsheet.getSheets(userData["spreadsheetID"])
        reqData = []
        reqData.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheets["Stat. " + userData["currentMonth"]],
                    "startRowIndex": 1,
                    "endRowIndex": 1000,
                    "startColumnIndex": 0,
                    "endColumnIndex": userData["daysCurMonth"] + 2
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        })

        reqData.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheets["Stat. " + userData["currentMonth"]],
                    "startRowIndex": 1,
                    "endRowIndex": 1 + len(userData["incomeCategories"]) + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": userData["daysCurMonth"] + 2
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.824,
                            "green": 0.96,
                            "blue": 0.753
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        })
        reqData.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheets["Stat. " + userData["currentMonth"]],
                    "startRowIndex": 1 + len(userData["incomeCategories"]) + 1 + 1,
                    "endRowIndex": 1 + len(userData["incomeCategories"]) + 1 + 1 + len(userData["costCategories"]) + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": userData["daysCurMonth"] + 2
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.921,
                            "green": 0.703,
                            "blue": 0.703
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        })
        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=userData["spreadsheetID"], body={
            'requests': reqData
        }).execute()

        value = []
        totalSumIncome = 0
        sumIncomeDayList = [0] * userData["daysCurMonth"]
        for x, i in enumerate(userData['incomeCategories']):
            totalSumIncome += int(userData['incomeCategories'][i][0])
            value.append([userCategories[i]['name'], userData['incomeCategories'][i][0]])
            for z in userData["incomeCategories"][i][1]:
                sumIncomeDayList[int(z)] += userData['incomeCategories'][i][1][z]
                value[-1].append(userData['incomeCategories'][i][1][z])
        value.insert(0, ['Общие доходы', totalSumIncome]+sumIncomeDayList)
        values.append(["Stat. " + userData["currentMonth"], 'ROWS', f'A2:{alf[userData["daysCurMonth"]]}{len(userData["incomeCategories"]) + 2 + 1}', value])

        value = []
        for i in userData['sources']:
            value.append([userData['sources'][i]])
        values.append(["Bills", 'ROWS', f'F2:F{len(userData["sources"]) + 2}', value])

        Spreadsheet.setValues(userData["spreadsheetID"], values)

    async def syncRecords(self, userData, userRecords):
        Spreadsheet.cleanValues(userData["spreadsheetID"], f'{userData["currentMonth"]}!A2:F100000')

        values = []

        value = []
        for i in userRecords:
            value.append(userRecords[i])

        values.append([userData["currentMonth"], 'ROWS',
                       f'A2:F{len(value) + 1}',
                       value])

        Spreadsheet.setValues(userData["spreadsheetID"], values)