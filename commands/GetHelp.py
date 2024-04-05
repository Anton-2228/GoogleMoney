import GlobalVariables


class GetHelp:
    def __init__(self):
        global help
        help = GlobalVariables.help

    async def execute(self, message):
        await message.answer(help)