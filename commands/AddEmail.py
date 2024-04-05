import re

import GlobalVariables
from Spreadsheet import Spreadsheet


class AddEmail:

    def __init__(self):
        global dp, data, categories, sources, Events
        dp = GlobalVariables.dispatcher
        data = GlobalVariables.data
        categories = GlobalVariables.categories
        sources = GlobalVariables.sources
        Events = GlobalVariables.Events

    async def execute(self, message):
        state = dp.current_state(user=message.from_user.id)

        if await state.get_state() == None:

            await state.set_state(Events.SET_EMAIL[0])
            await message.answer("Пришлите почту на домене @gmail")

        elif await state.get_state() == "set_email":

            if re.fullmatch('\w+@gmail.com', message.text) == None:
                await message.answer("Мне почта не нравится, давай другую")
            else:
                Spreadsheet.issueRights(data[str(message.from_user.id)]["spreadsheetID"], "user", "writer", data[str(message.from_user.id)]['email'])
                await state.reset_state()
                await message.answer("Права добавлены")