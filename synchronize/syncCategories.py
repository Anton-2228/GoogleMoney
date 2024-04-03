import re

from sheetAPIWrapper import Spreadsheet

def syncCat(userData, userCategories, sheetService, scope):
    cat = Spreadsheet.getValues(sheetService, userData["spreadsheetID"], scope)
    if "values" in cat:
        for z, row in enumerate(cat["values"]):
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
            elif ((row[0] != '' and row[4] != userCategories[row[0]]['name']) or row[0] == '') and row[4] in list(map(lambda x: userCategories[x]['name'], list(userCategories))):
                return f"В категориях в {z + 1} строке используется уже существующий Name"
            elif row[6] not in ['', '-'] and re.fullmatch('\d+', row[6]) == None:
                return f"В категориях в {z + 1} строке Limits должен быть записан натуральным числом, либо, если он отсутствует, дефисом('-')"
            elif row[6] not in ['', '-'] and row[2] == '1':
                return f"В категориях в {z + 1} строке стоит лимит у категории дохода"
            else:
                if row[0] != '':
                    userCategories[row[0]]['associations'] = []
                cross = []
                for i in userCategories:
                    for k in list(set(row[5].split() + [row[4]]).intersection(set(userCategories[i]['associations']))):
                        cross.append(k)
                if len(cross) != 0:
                    return f"В категориях в {z + 1} строке {', '.join(cross)} использован/ы повторно"
                else:
                    if row[0] == '':
                        row[0] = str(userData["categoryID"])
                        if row[2] == '1':
                            userData['incomeCategories'][row[0]] = [0, {}]
                            for v in range(int(userData["daysCurMonth"])):
                                userData['incomeCategories'][row[0]][1][str(v)] = 0
                        else:
                            userData['costCategories'][row[0]] = [0, {}]
                            for v in range(userData["daysCurMonth"]):
                                userData['costCategories'][row[0]][1][str(v)] = 0
                        userData["categoryID"] += 1
                    associations = row[5].split() + [row[4]]
                    associations = list(set(map(lambda x: x.lower(), associations)))
                    userCategories[row[0]] = {"active": row[1], 'income': row[2], 'cost': row[3], 'name': row[4], 'associations': associations, 'limit': row[6]}
    return True