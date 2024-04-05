import datetime

import GlobalVariables


def setStyleBaseLists(spreadsheetID):
    sheetService = GlobalVariables.sheetService
    startSheets = GlobalVariables.titles

    reqData = []
    for z, i in enumerate([len(startSheets["Categories"][0]), len(startSheets["Bills"][0])]):
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
        reqData.append({
            "updateSheetProperties": {
                "properties": {
                    "sheetId": z,
                    "gridProperties": {
                        "frozenRowCount": 1
                    }
                },
                "fields": "gridProperties(frozenRowCount)"
            }
        })

    response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
        'requests': reqData
    }).execute()

def setSecurityBaseLists(spreadsheetID):
    sheetService = GlobalVariables.sheetService
    startSheets = GlobalVariables.titles

    reqData = []
    for z, i in enumerate([len(startSheets["Categories"][0]), len(startSheets["Bills"][0])]):
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
        if z == 1:
            reqData.append({
                "addProtectedRange": {
                    "protectedRange": {
                        "range": {
                            "sheetId": z,
                            "startRowIndex": 0,
                            "startColumnIndex": 5,
                            "endColumnIndex": 6
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


def setStyleOperationLists(spreadsheetID, sheetId):
    sheetService = GlobalVariables.sheetService
    template = GlobalVariables.templateOperatios

    reqData = []

    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": len(template["template"][0])
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
    })

    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 0,
                "startColumnIndex": 0,
                "endColumnIndex": len(template["template"][0])
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
        }
    })

    reqData.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheetId,
                "gridProperties": {
                    "frozenRowCount": 1
                }
            },
            "fields": "gridProperties(frozenRowCount)"
        }
    })

    response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
        'requests': reqData
    }).execute()

def setSecurityOperationLists(spreadsheetID, sheetId):
    sheetService = GlobalVariables.sheetService
    template = GlobalVariables.templateOperatios

    reqData = []
    reqData.append({
        "addProtectedRange": {
            "protectedRange": {
                "range": {
                    "sheetId": sheetId,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(template["template"][0])
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

def setStyleStatisticsLists(spreadsheetID, sheetId, days):
    sheetService = GlobalVariables.sheetService
    template = GlobalVariables.templateStatistics

    reqData = []
    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 2,
                "endColumnIndex": len(days)+2
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
    })

    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": 2
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
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
        }
    })

    reqData.append({
        "repeatCell": {
            "range": {
                "sheetId": sheetId,
                "startRowIndex": 0,
                "startColumnIndex": 0,
                "endColumnIndex": len(days)+2
            },
            "cell": {
                "userEnteredFormat": {
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE"
                }
            },
            "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)"
        }
    })

    reqData.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheetId,
                "gridProperties": {
                    "frozenRowCount": 1
                }
            },
            "fields": "gridProperties(frozenRowCount)"
        }
    })

    response = sheetService.spreadsheets().batchUpdate(spreadsheetId=spreadsheetID, body={
        'requests': reqData
    }).execute()

def setSecurityStatisticsLists(spreadsheetID, sheetId, days):
    sheetService = GlobalVariables.sheetService
    template = GlobalVariables.templateStatistics

    reqData = []
    reqData.append({
        "addProtectedRange": {
            "protectedRange": {
                "range": {
                    "sheetId": sheetId,
                    "startRowIndex": 0,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(days)+2
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