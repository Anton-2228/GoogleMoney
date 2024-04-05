import asyncio
import json

import Init

from aiogram.utils.helper import Helper, HelperMode, ListItem

dispatcher = Init.createDispatcher()
sheetService = Init.createSheetService()
driveService = Init.createDriveService()
counter = asyncio.get_event_loop()

class Events(Helper):
    mode = HelperMode.snake_case

    CHOICE_TABLE_NAME = ListItem()
    SET_EMAIL = ListItem()
    CORRECT_TABLE = ListItem()
    COMFIRM_DELETE = ListItem()
    COMFIRM_CHANGE_DATE_RESET = ListItem()

with open('data/title.json', 'r') as file:
    titles = json.load(file)

with open('data/templateOperatios.json', 'r') as file:
    templateOperatios = json.load(file)

with open('data/templateStatistics.json', 'r') as file:
    templateStatistics = json.load(file)

with open('data/data.json', 'r') as file:
    data = json.loads(file.read())

with open('data/categories.json', 'r') as file:
    categories = json.loads(file.read())

with open('data/sources.json', 'r') as file:
    sources = json.loads(file.read())

with open('data/records.json', 'r') as file:
    records = json.loads(file.read())

with open('data/help.txt', 'r', encoding='utf-8') as file:
    help = file.read()

daysUntilNextMonth = {1: 31,
                      2: 28,
                      3: 31,
                      4: 30,
                      5: 31,
                      6: 30,
                      7: 31,
                      8: 31,
                      9: 30,
                      10: 31,
                      11: 30,
                      12: 31}

alf = {0:'C',
       1:'D',
       2:'E',
       3:'F',
       4:'G',
       5:'H',
       6:'I',
       7:'J',
       8:'K',
       9:'L',
       10:'M',
       11:'N',
       12:'O',
       13:'P',
       14:'Q',
       15:'R',
       16:'S',
       17:'T',
       18:'U',
       19:'V',
       20:'W',
       21:'X',
       22:'Y',
       23:'Z',
       24:'AA',
       25:'AB',
       26:'AC',
       27:'AD',
       28:'AE',
       29:'AF',
       30:'AG',
       31:'AH'}

globTimer = Init.createTimer()

commandManager = Init.createCommandManager()