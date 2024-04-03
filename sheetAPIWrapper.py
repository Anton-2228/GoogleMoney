import datetime
import copy
import json

class Spreadsheet:

    # Создание таблицы
    @staticmethod
    def createTable(sheetService, startSheets, title):

        sheets = []
        #sheetsNames = []
        for x, i in enumerate(startSheets):
            sheet = {'properties': {'sheetType': 'GRID',
                                       'sheetId': x,
                                       'title': i}}
            sheets.append(sheet)
            #sheetsNames.append(i)

        spreadsheet = sheetService.spreadsheets().create(body={
            'properties': {'title': title, 'locale': 'ru_RU'},
            'sheets': sheets
        }).execute()

        spreadsheetID = spreadsheet["spreadsheetId"]

        for list in startSheets:
            values = startSheets[list][0]
            Spreadsheet.setValues(sheetService, spreadsheetID, [[list, "ROWS", f"A{1}:{len(values)}", [values]]])
            widths = startSheets[list][1]
            values = []
            for x, width in enumerate(widths):
                values.append([list, x, x+1, width])
            Spreadsheet.setWidthColumn(sheetService, spreadsheetID, values)

        Spreadsheet.setStyle(sheetService, spreadsheetID)
        Spreadsheet.setSecurity(sheetService, spreadsheetID)

        print(spreadsheet["spreadsheetUrl"])
        return spreadsheetID

    # Выдача прав редактора
    @staticmethod
    def issueRights(driveService, spreadsheetID, type, role, emailAddres=None):
        shareRes = driveService.permissions().create(
            fileId=spreadsheetID,
            body={'type': type, 'role': role, 'emailAddress': emailAddres},
            fields='id'
        ).execute()

    # data = [title]
    @staticmethod
    def addNewSheet(sheetService, spreadsheetID, data, delta):
        curDate = data[0]
        data[0] = str(data[0])

        reqData = []
        reqData.append({
            "addSheet": {
                "properties": {
                    "title": data[0],
                    'gridProperties': {'columnCount': 50}
                }
            }
        })
        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            "requests": reqData
        }).execute()

        values = []
        values.append([data[0], 'ROWS', f'A1:{len(data[1][0])}', [data[1][0]]])

        width = []
        days = []
        for i in range(delta.days):
            days.append(str(curDate + datetime.timedelta(days=i)))
            width.append([data[0], 11+i, 12+i, 45])
        values.append([data[0], 'ROWS', f'L1:{len(days)}', [days]])

        for x, z in enumerate(data[1][1]):
            width.append([data[0], x, x+1, z])

        Spreadsheet.setValues(sheetService, spreadsheetID, values)
        Spreadsheet.setWidthColumn(sheetService, spreadsheetID, width)

        # Установка стиля
        sheets = Spreadsheet.getSheets(sheetService, spreadsheetID)
        reqData = []
        loc = {
            "repeatCell": {
                "range": {
                    "sheetId": sheets[str(datetime.date.today())],
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 11,
                    "endColumnIndex": 11 + len(days)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.9,
                            "green": 0.9,
                            "blue": 0.9
                        },
                        "textFormat": {
                            "fontSize": 10,
                            "bold": True
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "textRotation": {
                            "angle": -90
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,textRotation,verticalAlignment)"
            }
        }
        reqData.append(loc)




        loc = {
            "repeatCell": {
                "range": {
                    "sheetId": sheets[str(datetime.date.today())],
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.9,
                            "green": 0.9,
                            "blue": 0.9
                        },
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                        "textFormat": {
                            "fontSize": 10,
                            "bold": True
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
            }
        }
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["repeatCell"]["range"]["startColumnIndex"] = 6
        loc["repeatCell"]["range"]["endColumnIndex"] = 8
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["repeatCell"]["range"]["startColumnIndex"] = 9
        loc["repeatCell"]["range"]["endColumnIndex"] = 11
        reqData.append(loc)

        loc = {
            "repeatCell": {
                "range": {
                    "sheetId": sheets[str(datetime.date.today())],
                    "startRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 5
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment)"
            }
        }
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["repeatCell"]["range"]["startColumnIndex"] = 6
        loc["repeatCell"]["range"]["endColumnIndex"] = 8
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["repeatCell"]["range"]["startColumnIndex"] = 9
        loc["repeatCell"]["range"]["endColumnIndex"] = 11 + len(days)
        reqData.append(loc)

        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            'requests': reqData
        }).execute()

        # Установка защиты
        reqData = []
        loc = {
            "addProtectedRange": {
                "protectedRange": {
                    "range": {
                        "sheetId": sheets[str(datetime.date.today())],
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": 5
                    },
                    "warningOnly": False,
                    "editors": {
                        "users": ["stepansokoladov@gmail.com"]
                    }
                }
            }
        }
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["addProtectedRange"]["protectedRange"]["range"]["startColumnIndex"] = 6
        loc["addProtectedRange"]["protectedRange"]["range"]["endColumnIndex"] = 8
        reqData.append(loc)
        loc = copy.deepcopy(loc)
        loc["addProtectedRange"]["protectedRange"]["range"]["startColumnIndex"] = 9
        loc["addProtectedRange"]["protectedRange"]["range"]["endColumnIndex"] = 11 + len(days)
        reqData.append(loc)

        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            'requests': reqData
        }).execute()

    # Изменение ширины колонки
    # data = [[sheetName, startIndex, endIndex, width]]
    @staticmethod
    def setWidthColumn(sheetService, spreadsheetID, data):
        sheets = Spreadsheet.getSheets(sheetService, spreadsheetID)
        reqData = []
        for i in data:
            loc = {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheets[i[0]],
                            "dimension": "COLUMNS",
                            "startIndex": i[1],
                            "endIndex": i[2]
                        },
                        "properties": {
                            "pixelSize": i[3]
                        },
                        "fields": "pixelSize"
                    }
                }
            reqData.append(loc)
        results = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            "requests": reqData
        }).execute()

    # Установка значений ячеек
    # data = [[sheetName, dimension, range, values]]
    @staticmethod
    def setValues(sheetService, spreadsheetID, data):
        reqData = []
        for i in data:
            loc = {"range": f"{i[0]}!{i[2]}",
                 "majorDimension": i[1],
                 "values": i[3]}
            reqData.append(loc)
        results = sheetService.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetID, body={
            "valueInputOption": "USER_ENTERED",
            "data": reqData
        }).execute()

    @staticmethod
    def cleanValues(sheetService, spreadsheetID, range):
        response = sheetService.spreadsheets().values().clear(spreadsheetId=spreadsheetID, range=range).execute()

    # data = [[sheetName, startRowIndex, startColumnIndex, endColumnIndex]]
    @staticmethod
    def setSecurity(sheetService, spreadsheetID):
        reqData = []
        for z, i in enumerate([7,5]):
            reqData.append({
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": z,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": i
                        },
                        "warningOnly": False,
                        "editors": {
                            "users": []
                        }
                    }
                }
            })
            reqData.append({
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": z,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "warningOnly": False,
                        "editors": {
                            "users": []
                        }
                    }
                }
            })

        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            'requests': reqData
        }).execute()

    @staticmethod
    def setStyle(sheetService, spreadsheetID):
        reqData = []
        for z, i in enumerate([7,5]):
            reqData.append({
                "repeatCell": {
                    "range": {
                        "sheetId": z,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": i
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 0.9,
                                "green": 0.9,
                                "blue": 0.9
                            },
                            "horizontalAlignment": "CENTER",
                            "textFormat": {
                                "fontSize": 10,
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor, textFormat, horizontalAlignment)"
                }
            })
            reqData.append({
                "repeatCell": {
                    "range": {
                        "sheetId": z,
                        "startRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": i
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER"
                        }
                    },
                    "fields": "userEnteredFormat(horizontalAlignment)"
                }
            })

        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            'requests': reqData
        }).execute()

    @staticmethod
    def getValues(sheetService, spreadsheetID, range):
        result = sheetService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=range).execute()
        return result

    @staticmethod
    def getSheets(sheetService, spreadsheetID):
        response = sheetService.spreadsheets().get(spreadsheetId=spreadsheetID).execute()
        sheets = {}
        for i in response["sheets"]:
            sheets[i['properties']['title']] = i['properties']['sheetId']
        return sheets