import datetime

import GlobalVariables
import SpreadsheetSetStyles


class Spreadsheet:

    # Создание таблицы
    @staticmethod
    def createTable(title, email):
        sheetService = GlobalVariables.sheetService
        startSheets = GlobalVariables.titles

        sheets = []
        for x, i in enumerate(startSheets):
            sheet = {'properties': {'sheetType': 'GRID',
                                    'sheetId': x,
                                    'title': i}}
            sheets.append(sheet)

        spreadsheet = sheetService.spreadsheets().create(body={
            'properties': {'title': title, 'locale': 'ru_RU'},
            'sheets': sheets
        }).execute()

        spreadsheetID = spreadsheet["spreadsheetId"]

        values = []
        widthsValues = []
        for list in startSheets:
            value = startSheets[list][0]
            values.append([list, "ROWS", f"A{1}:{len(value)}", [value]])
            widths = startSheets[list][1]
            for x, width in enumerate(widths):
                widthsValues.append([list, x, x+1, width])
        Spreadsheet.setWidthColumn(spreadsheetID, widthsValues)
        Spreadsheet.setValues(spreadsheetID, values)

        SpreadsheetSetStyles.setStyleBaseLists(spreadsheetID)
        SpreadsheetSetStyles.setSecurityBaseLists(spreadsheetID)

        Spreadsheet.issueRights(spreadsheetID, 'user', 'writer', email)

        return spreadsheetID

    # Выдача прав редактора
    @staticmethod
    def issueRights(spreadsheetID, type, role, emailAddres=None):
        driveService = GlobalVariables.driveService

        shareRes = driveService.permissions().create(
            fileId=spreadsheetID,
            body={'type': type, 'role': role, 'emailAddress': emailAddres},
            fields='id'
        ).execute()

    @staticmethod
    def addNewOperationsSheet(spreadsheetID, currentMonth):
        sheetService = GlobalVariables.sheetService
        template = GlobalVariables.templateOperatios["template"]

        reqData = []
        reqData.append({
            "addSheet": {
                "properties": {
                    "title": str(currentMonth)
                }
            }
        })
        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            "requests": reqData
        }).execute()

        values = []
        values.append([str(currentMonth), 'ROWS', f'A1:{len(template[0])}', [template[0]]])

        '''
        width = []
        days = []
        for i in range(delta.days):
            days.append(str(currentMonth + datetime.timedelta(days=i)))
            width.append([str(currentMonth), 11 + i, 12 + i, 45])
        values.append([str(currentMonth), 'ROWS', f'L1:{len(days)}', [days]])
        '''

        width = []
        for x, z in enumerate(template[1]):
            width.append([str(currentMonth), x, x + 1, z])

        Spreadsheet.setValues(spreadsheetID, values)
        Spreadsheet.setWidthColumn(spreadsheetID, width)

        sheets = Spreadsheet.getSheets(spreadsheetID)
        SpreadsheetSetStyles.setStyleOperationLists(spreadsheetID, sheets[str(currentMonth)])
        SpreadsheetSetStyles.setSecurityOperationLists(spreadsheetID, sheets[str(currentMonth)])

    @staticmethod
    def addNewStatisticsSheet(spreadsheetID, currentMonth, delta):
        sheetService = GlobalVariables.sheetService
        template = GlobalVariables.templateStatistics["template"]

        reqData = []
        reqData.append({
            "addSheet": {
                "properties": {
                    "title": "Stat. " + str(currentMonth),
                    'gridProperties': {'columnCount': 50}
                }
            }
        })
        response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
            "requests": reqData
        }).execute()

        values = []
        values.append(["Stat. " + str(currentMonth), 'ROWS', f'A1:3', [template[0]]])
        width = []
        for x, i in enumerate(template[1]):
            width.append(["Stat. " + str(currentMonth), x, x+1, i])
        days = []
        for i in range(delta.days):
            days.append(str(currentMonth + datetime.timedelta(days=i)))
            width.append(["Stat. " + str(currentMonth), i+2, i + 3, 45])
        values.append(["Stat. " + str(currentMonth), 'ROWS', f'C1:{len(days)}', [days]])

        Spreadsheet.setValues(spreadsheetID, values)
        Spreadsheet.setWidthColumn(spreadsheetID, width)

        sheets = Spreadsheet.getSheets(spreadsheetID)
        SpreadsheetSetStyles.setStyleStatisticsLists(spreadsheetID, sheets["Stat. " + str(currentMonth)], days)
        SpreadsheetSetStyles.setSecurityStatisticsLists(spreadsheetID, sheets["Stat. " + str(currentMonth)], days)

    @staticmethod
    def setWidthColumn(spreadsheetID, data):
        sheetService = GlobalVariables.sheetService

        sheets = Spreadsheet.getSheets(spreadsheetID)
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
    # data_files = [[sheetName, dimension, range, values]]
    @staticmethod
    def setValues(spreadsheetID, data):
        sheetService = GlobalVariables.sheetService

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
    def cleanValues(spreadsheetID, range):
        sheetService = GlobalVariables.sheetService
        response = sheetService.spreadsheets().values().clear(spreadsheetId=spreadsheetID, range=range).execute()

    @staticmethod
    def getValues(spreadsheetID, range):
        sheetService = GlobalVariables.sheetService

        result = sheetService.spreadsheets().values().get(spreadsheetId=spreadsheetID, range=range).execute()
        return result

    @staticmethod
    def getSheets(spreadsheetID):
        sheetService = GlobalVariables.sheetService

        response = sheetService.spreadsheets().get(spreadsheetId=spreadsheetID).execute()
        sheets = {}
        for i in response["sheets"]:
            sheets[i['properties']['title']] = i['properties']['sheetId']
        return sheets