import GlobalVariables

class GetTable:
    def __init__(self):
        global data
        data = GlobalVariables.data

    async def execute(self, message):
        spreadsheetID = data[str(message.from_user.id)]["spreadsheetID"]
        await message.answer(f"Ссылка на таблицу:\nhttps://docs.google.com/spreadsheets/d/{spreadsheetID}/edit#gid=0")