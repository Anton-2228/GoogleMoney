import json

import GlobalVariables

def saveData():
    data = GlobalVariables.data
    categories = GlobalVariables.categories
    sources = GlobalVariables.sources
    records = GlobalVariables.records
    # Я ЗНАЮ ЧТО ЭТО ПИЗДЕЦ, ВСЕ БУДЕТ ПЕРЕДЕЛАНО
    with open('data/data.json', 'w+') as file:
        json.dump(data, file)
    with open('data/categories.json', 'w+') as file:
        json.dump(categories, file)
    with open('data/sources.json', 'w+') as file:
        json.dump(sources, file)
    with open('data/records.json', 'w+') as file:
        json.dump(records, file)