import re

from sheetAPIWrapper import Spreadsheet

def syncSour(userData, userSources, sheetService, range):
    sour = Spreadsheet.getValues(sheetService, userData["spreadsheetID"], range)
    if "values" in sour:
        for z, row in enumerate(sour["values"]):
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
            elif ((row[0] != '' and row[2] != userSources[row[0]]['name']) or row[0] == '') and row[2] in list(map(lambda x: userSources[x]['name'], list(userSources))):
                return f"В источниках в {z + 1} строке используется уже существующий Name"
            elif len(row[2].split()) > 1:
                return f"В источниках в {z + 1} строке Name записан не одним словом"
            elif re.fullmatch('-?\d+', row[4])==None:
                return f"В источниках в {z + 1} строке Balance должен быть целым числом"
            else:
                if row[0] != '':
                    userSources[row[0]]['associations'] = []
                cross = []
                for i in userSources:
                    for k in list(set(row[3].split() + [row[2]]).intersection(set(userSources[i]['associations']))):
                        cross.append(k)
                if len(cross) != 0:
                    return f"В источниках в {z + 1} строке {', '.join(cross)} использован/ы повторно"
                else:
                    if row[0] == '':
                        row[0] = str(userData['sourceID'])
                        userData['sources'][row[0]] = int(row[4])
                        userData["sourceID"] += 1
                    else:
                        delta = int(row[4]) - int(userSources[row[0]]['startBalance'])
                        userData['sources'][row[0]] += delta
                    associations = row[3].split() + [row[2]]
                    associations = list(set(map(lambda x: x.lower(), associations)))
                    userSources[row[0]] = {"active": row[1], "name": row[2], 'associations': associations, 'startBalance': row[4]}
    return True