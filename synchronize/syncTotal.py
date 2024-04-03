from sheetAPIWrapper import Spreadsheet

alf = {0:'L',
       1:'M',
       2:'N',
       3:'O',
       4:'P',
       5:'Q',
       6:'R',
       7:'S',
       8:'T',
       9:'U',
       10:'V',
       11:'W',
       12:'X',
       13:'Y',
       14:'Z',
       15:'AA',
       16:'AB',
       17:'AC',
       18:'AD',
       19:'AE',
       20:'AF',
       21:'AG',
       22:'AH',
       23:'AI',
       24:'AJ',
       25:'AK',
       26:'AL',
       27:'AM',
       28:'AN',
       29:'AO',
       30:'AP',
       31:'AQ'}

def syncTotal(userData, userCategories, userSources, sheetService):
    #Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!G2:H100000')
    #Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!J2:K100000')
    #Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!M2:N100000')
    Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!J2:K100000')
    Spreadsheet.cleanValues(sheetService, userData["spreadsheetID"], f'{userData["currentMonth"]}!{alf[userData["daysCurMonth"]]}2:{alf[userData["daysCurMonth"]]}1000')

    values = []

    value = []
    valueData = []
    totalSumCost = 0
    daySumCost = 0
    for i in userData['costCategories']:
        totalSumCost += int(userData['costCategories'][i][0])
        value.append([userCategories[i]['name'], userData['costCategories'][i][0]])
        daySumCost += int(userData['costCategories'][i][1][str(userData["actualDay"])])
        valueData.append([userData['costCategories'][i][1][str(userData["actualDay"])]])
    value.insert(0, ['Общие расходы', totalSumCost])
    valueData.insert(0, [daySumCost])
    values.append([userData["currentMonth"], 'ROWS', f'J{len(userData["incomeCategories"]) + 2 + 1 + 1}:K{len(userData["incomeCategories"]) + len(userData["costCategories"]) + 2 + 1 + 1}', value])
    values.append([userData["currentMonth"], 'ROWS', f'{alf[userData["actualDay"]]}{len(userData["incomeCategories"]) + 2 + 1 + 1}:{alf[userData["daysCurMonth"]]}{len(userData["incomeCategories"]) + len(userData["costCategories"]) + 2 + 1 + 1}', valueData])

    sheets = Spreadsheet.getSheets(sheetService, userData["spreadsheetID"])
    reqData = []
    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheets[userData["currentMonth"]],
                "startRowIndex": 1,
                "endRowIndex": 1+len(userData["incomeCategories"])+1,
                "startColumnIndex": 9,
                "endColumnIndex": 9+userData["daysCurMonth"]+2
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
                "sheetId": sheets[userData["currentMonth"]],
                "startRowIndex": 1+len(userData["incomeCategories"])+1+1,
                "endRowIndex": 1+len(userData["incomeCategories"])+1+1+len(userData["costCategories"]) + 1,
                "startColumnIndex": 9,
                "endColumnIndex": 9+userData["daysCurMonth"] + 2
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
    valueData = []
    totalSumIncome = 0
    daySumIncome = 0
    for x, i in enumerate(userData['incomeCategories']):
        totalSumIncome += int(userData['incomeCategories'][i][0])
        value.append([userCategories[i]['name'], userData['incomeCategories'][i][0]])
        daySumIncome += int(userData['incomeCategories'][i][1][str(userData["actualDay"])])
        valueData.append([userData['incomeCategories'][i][1][str(userData["actualDay"])]])
    value.insert(0, ['Общие доходы', totalSumIncome])
    valueData.insert(0, [daySumIncome])
    values.append([userData["currentMonth"], 'ROWS', f'J2:K{len(userData["incomeCategories"]) + 2 + 1}', value])
    values.append([userData["currentMonth"], 'ROWS', f'{alf[userData["actualDay"]]}2:{alf[userData["daysCurMonth"]]}{len(userData["incomeCategories"]) + 2 + 1}', valueData])

    value = []
    for i in userData['sources']:
        value.append([userSources[i]['name'], userData['sources'][i]])
    values.append([userData["currentMonth"], 'ROWS', f'G2:H{len(userData["sources"]) + 2}', value])

    Spreadsheet.setValues(sheetService, userData["spreadsheetID"], values)